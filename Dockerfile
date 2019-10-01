FROM python:3.7-alpine

# copy the script
COPY ./opendata-downloader.py /

# download some example data
CMD python ./opendata-downloader.py --help