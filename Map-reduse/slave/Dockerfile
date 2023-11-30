FROM python

WORKDIR /slave
COPY . /slave
RUN python3 -m pip install beautifulsoup4 bottle requests textblob
RUN python3 -m textblob.download_corpora

ENTRYPOINT ["python", "app/main.py"]