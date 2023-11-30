FROM python

WORKDIR /master
COPY . /master

ENTRYPOINT ["python", "app/main.py", "--links_file", "links.txt", "--db_path", "data"]