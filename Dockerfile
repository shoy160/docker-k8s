FROM python:3-alpine

# 设置时区
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories \
    && apk add tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone \
    && apk del tzdata

COPY . /publish
RUN pip install -r /publish/requirements.txt -i https://pypi.douban.com/simple
WORKDIR /publish
EXPOSE 8080
ENTRYPOINT [ "python","server.py" ]

# docker build -t docker-k8s .
# docker run --name=docker-k8s -e REGISTRY_DATA_DIR= -e REGISTRY_URL= \
# -v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config \
# -p 9000:8080 -d docker-k8s

# docker run --name=docker-k8s -e REGISTRY_DATA_DIR= -e REGISTRY_URL="http://192.168.0.231:5000" -v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config -p 9000:8080 -d docker-k8s

# 镜像文件地址
# -e REGISTRY_DATA_DIR=
# 镜像API地址,如http://192.168.0.231:5000
# -e REGISTRY_URL=
# Docker镜像仓库，用于k8s对比和更新,如：docker.dev:5000
# -e DOCKER_REGISTRY=
# 运行kubectl
# -v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config

# 完整实例
# docker run --name=docker-k8s -e REGISTRY_DATA_DIR=/docker-registry -e DOCKER_REGISTRY="docker.dev:5000" -e REGISTRY_URL="http://192.168.0.231:5000" -v /data/nfs/docker-registry/docker/registry/v2/:/docker-registry -v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config -p 9000:8080 -d docker-k8s