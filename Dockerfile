FROM python:3.7-alpine

# copy the script
COPY ./opendata-downloader.py /

# display help
CMD python ./opendata-downloader.py --help