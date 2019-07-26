FROM python:3-alpine

COPY . /publish
RUN pip install -r /publish/requirements.txt -i https://pypi.douban.com/simple
WORKDIR /publish
EXPOSE 8080
ENTRYPOINT [ "python","server.py" ]

# 镜像文件地址
# -e REGISTRY_DATA_DIR=
# 镜像地址
# -e REGISTRY_URL=
# 运行kubectl
# -v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config