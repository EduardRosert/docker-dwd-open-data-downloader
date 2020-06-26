# Docker DWD Open Data Downloader
A simple python script to download some nwp data from DWD's Open Data File Server https://opendata.dwd.de, that can be run in a Docker container.

## Installation instructions
This describes how you create the docker image.

Clone this repo:
```bash
git clone https://github.com/EduardRosert/docker-dwd-open-data-downloader.git
```
Assuming you have docker already installed on your machine, switch to repo and type ``make``:
```bash
cd docker-dwd-open-data-downloader/
make
```
Check if image creation was successful by typing
```bash
docker images
```
You should see something like this on top:
```
REPOSITORY                                         TAG                 IMAGE ID            CREATED             SIZE
eduardrosert/dwd-open-data-downloader   latest              ba671cf17dc3        18 seconds ago      98.7MB
...
```

## Test the image
Test the image and see the command line options by typing
```bash
docker run --rm -i -t eduardrosert/dwd-open-data-downloader:latest python /opendata-downloader.py --help
```
Output:
```
usage: opendata-downloader.py [-h] --model
                              {cosmo-d2,cosmo-d2-eps,icon,icon-eps,icon-eu,icon-eu-eps,icon-d2,icon-d2-eps}
                              [--grid {icosahedral,regular-lat-lon,rotated-lat-lon}]
                              [--get-latest-timestamp]
                              [--single-level-fields shortName [shortName ...]]
                              [--min-time-step MINTIMESTEP]
                              [--max-time-step MAXTIMESTEP]
                              [--directory DESTFILEPATH]
                              [--http-proxy proxy_name_or_ip:port] [-v]

A tool to download grib model data from DWD's open data server
https://opendata.dwd.de .

optional arguments:
  -h, --help            show this help message and exit
  --model {cosmo-d2,cosmo-d2-eps,icon,icon-eps,icon-eu,icon-eu-eps,icon-d2,icon-d2-eps}
                        the model name
  --grid {icosahedral,regular-lat-lon,rotated-lat-lon}
                        the grid type
  --get-latest-timestamp
                        Returns the latest available timestamp for the
                        specified model.
  --single-level-fields shortName [shortName ...]
                        one or more single-level model fields that should be
                        donwloaded, e.g. t_2m, tmax_2m, clch, pmsl, ...
  --min-time-step MINTIMESTEP
                        the minimum forecast time step to download (default=0)
  --max-time-step MAXTIMESTEP
                        the maximung forecast time step to download, e.g. 12
                        will download time steps from min-time-step - 12. If
                        no max-time-step was defined, no data will be
                        downloaded.
  --directory DESTFILEPATH
                        the download directory
  --http-proxy proxy_name_or_ip:port
                        the http proxy url and port
  -v, --verbose         increase output verbosity
```

# Download data
You can download some custom data by running:
```bash
docker run --rm -i -t eduardrosert/dwd-open-data-downloader:latest python /opendata-downloader.py --model icon-eu --single-level-fields t_2m --max-time-step 5 -v --directory /
```
You should see verbose output like this:
```
[opendata-downloader.py:45 - downloadAndExtractBz2FileFromUrl() ] downloading file: 'https://opendata.dwd.de/weather/nwp/icon-eu/grib/06/t_2m/icon-eu_europe_regular-lat-lon_single-level_2019100106_000_T_2M.grib2.bz2'
[opendata-downloader.py:58 - downloadAndExtractBz2FileFromUrl() ] saving file as: '/icon-eu_europe_regular-lat-lon_single-level_2019100106_000_T_2M.grib2'
[opendata-downloader.py:61 - downloadAndExtractBz2FileFromUrl() ] Done.
[opendata-downloader.py:45 - downloadAndExtractBz2FileFromUrl() ] downloading file: 'https://opendata.dwd.de/weather/nwp/icon-eu/grib/06/t_2m/icon-eu_europe_regular-lat-lon_single-level_2019100106_001_T_2M.grib2.bz2'
...
```