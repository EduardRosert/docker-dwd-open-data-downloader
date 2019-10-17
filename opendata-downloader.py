#!/usr/bin/env python
""" opendata-downloader.py

 Script to download and extract grib files from DWD's open data file server https://opendata.dwd.de

 Author:
    Eduard Rosert
 Version history:
    0.2, 2019-10-17, added --get-latest-timestamp, --min-timestamp option
    0.1, 2019-10-01, initial version
"""

try:
    import argparse
    import sys
    import csv
    import urllib.request
    import bz2
    import json
    import math
    import os
    from datetime import datetime, timedelta, timezone
    import logging as log
except ImportError as ie:
    print("required libraries could not be found:")
    print(ie)
    sys.exit(1)


def configureHttpProxyForUrllib( proxySettings = {'http': 'proxyserver:8080'} ):
    proxy = urllib.request.ProxyHandler(proxySettings)
    opener = urllib.request.build_opener(proxy)
    urllib.request.install_opener(opener)


def getMostRecentModelTimestamp(waitTimeMinutes=360, modelIntervalHours=3):
    # model data becomes available approx 1.5 hours (90minutes) after a model run
    # cosmo-d2 model and icon-eu run every 3 hours
    now = datetime.utcnow() - timedelta(minutes=waitTimeMinutes)
    latestAvailableUTCRun = int(math.floor(now.hour/modelIntervalHours) * modelIntervalHours)
    modelTimestamp = datetime( now.year, now.month, now.day, latestAvailableUTCRun)
    return modelTimestamp

def downloadAndExtractBz2FileFromUrl( url , destFilePath=None, destFileName=None):
    log.info("downloading file: '{0}'".format(url))

    if destFileName == "" or destFileName == None:
        # strip the filename from the url and remove the bz2 extension
        destFileName = url.split('/')[-1].split('.bz2')[0]

    if destFilePath == "" or destFilePath == None:
        destFilePath = os.getcwd()

    resource = urllib.request.urlopen(url)
    compressedData = resource.read()
    binaryData = bz2.decompress(compressedData)
    fullFilePath = os.path.join(destFilePath, destFileName)
    log.info("saving file as: '{0}'".format(fullFilePath))
    with open(fullFilePath, 'wb') as outfile:
        outfile.write(binaryData)
    log.info("Done.")

def getGribFileUrl(model="icon-eu", param="t_2m", timestep=0, timestamp=getMostRecentModelTimestamp(waitTimeMinutes=180, modelIntervalHours=12)):
    modelrun = "{0:02d}".format(timestamp.hour)
    scope = "unknown"
    model = model.lower()
    if model == "icon-eu":
        scope = "europe"
    elif model == "cosmo-d2":
        scope = "germany"
    urlPattern = "https://opendata.dwd.de/weather/nwp/{0}/grib/{4}/{2}/{0}_{6}_regular-lat-lon_single-level_{1}_{3:03d}_{5}.grib2.bz2"
    return urlPattern.format(
                            model,
                            timestamp.strftime("%Y%m%d"+ modelrun ), 
                            param.lower(), 
                            timestep, 
                            modelrun, 
                            param.upper(), 
                            scope )

def downloadGribData( model="icon-eu", param="t_2m", timestep=0, timestamp=getMostRecentModelTimestamp(), destFilePath=None, destFileName=None ):
    dataUrl=getGribFileUrl(model=model, param=param, timestep=timestep, timestamp=timestamp)#

    downloadAndExtractBz2FileFromUrl(dataUrl, destFilePath=destFilePath, destFileName=destFileName)

def downloadGribDataSequence(model="icon-eu", param="t_2m", minTimeStep=0, maxTimeStep=12, timestamp=getMostRecentModelTimestamp(), destFilePath=None ):
    #download data from open data server for the next x steps
    for timestep in range(minTimeStep, maxTimeStep+1):
        downloadGribData(model=model, param=param, timestep=timestep, timestamp=timestamp, destFilePath=destFilePath)

def formatDateIso8601(date):
    return date.replace(microsecond=0,tzinfo=timezone.utc).isoformat()

def getTimestampString(date):
    modelrun = "{0:02d}".format(date.hour)
    return date.strftime("%Y%m%d"+ modelrun )

parser = argparse.ArgumentParser(
    description='A tool to download grib model data from DWD\'s open data server https://opendata.dwd.de .',
    add_help=True)

parser.add_argument('--model', choices=['cosmo-d2', 'icon-eu'],
                    dest='model',
                    type=str,
                    required=True,
                    help='the model name')

parser.add_argument('--get-latest-timestamp',
                    dest='getLatestTimestamp',
                    action='store_true',
                    help='Returns the latest available timestamp for the specified model.')


# use it like this: --single-level-fields t_2m pmsl clch ...
parser.add_argument('--single-level-fields', 
                    dest='params',
                    nargs='+', 
                    metavar='shortName',
                    type=str,
                    default=['t_2m'],
                    help='one or more single-level model fields that should be donwloaded, e.g. t_2m, tmax_2m, clch, pmsl, ...')

parser.add_argument('--min-time-step', dest='minTimeStep', default=0, type=int,
                    help='the minimum forecast time step to download (default=0)')

parser.add_argument('--max-time-step', dest='maxTimeStep', default=-1, type=int,
                    help='the maximung forecast time step to download, e.g. 12 will download time steps from min-time-step - 12. If no max-time-step was defined, no data will be downloaded.')

parser.add_argument('--directory', dest='destFilePath', default=os.getcwd(),
                    help='the download directory')

parser.add_argument('--http-proxy', dest='proxy', metavar='proxy_name_or_ip:port', required=False,
                    help='the http proxy url and port')

parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_const", dest="loglevel", const=log.INFO)

"""
usage: opendata-downloader.py [-h] --model {cosmo-d2,icon-eu}
                              --single-level-fields shortName [shortName ...]
                              [--max-time-step MAXTIMESTEP]
                              [--directory DESTFILEPATH]
                              [--http-proxy proxy_name_or_ip:port] [-v]

A tool to download grib model data from DWD's open data server
https://opendata.dwd.de .

optional arguments:
  -h, --help            show this help message and exit
  --model {cosmo-d2,icon-eu}
                        the model name
  --single-level-fields shortName [shortName ...]
                        one or more single-level model fields that should be
                        donwloaded, e.g. t_2m, tmax_2m, clch, pmsl, ...
  --max-time-step MAXTIMESTEP
                        the maximung forecast time step to download, e.g. 12
                        will download time steps 0 - 12
  --directory DESTFILEPATH
                        the download directory
  --http-proxy proxy_name_or_ip:port
                        the http proxy url and port
  -v, --verbose         increase output verbosity
"""
if __name__ == "__main__":
    logformat = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

    args = parser.parse_args()
    if args.loglevel:
        log.basicConfig(format=logformat, level=log.DEBUG) # verbose
    else:
        log.basicConfig(format=logformat, level=log.ERROR) # default
    

    if args.proxy:
        #configure proxy
        configureHttpProxyForUrllib( proxySettings = {'http': args.proxy } ) 

    #add custom dialect for csv export
    csv.register_dialect('excel-semicolon', delimiter=';', quoting=csv.QUOTE_ALL, lineterminator='\r\n')

    # wait 5 hrs (=300 minutes) after a model run for icon-eu data
    # and 1,5 hrs (=90 minute) for cosmo-d2, just to be sure
    waitTimeMinutes=300
    if args.model == "cosmo-d2":
        waitTimeMinutes = 90
    latestTimestamp = getMostRecentModelTimestamp(waitTimeMinutes=waitTimeMinutes, modelIntervalHours=3)

    #download data
    for param in args.params:
        downloadGribDataSequence(model=args.model, param=param, minTimeStep=args.minTimeStep, maxTimeStep=args.maxTimeStep, timestamp=latestTimestamp, destFilePath=args.destFilePath )

    if args.getLatestTimestamp:
        print(getTimestampString(latestTimestamp))