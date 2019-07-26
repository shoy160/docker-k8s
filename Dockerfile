FROM python:3-alpine

COPY . /publish
RUN pip install -r /publish/requirements.txt -i https://pypi.douban.com/simple
WORKDIR /publish
EXPOSE 8080
ENTRYPOINT [ "python","server.py" ]