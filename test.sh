#!/bin/bash
(docker rm -f docker-k8s && docker rmi docker-k8s) || echo 'not exists'

docker build -t docker-k8s . && \
docker run --name=docker-k8s -e REGISTRY_DATA_DIR=/docker-registry \
-e DOCKER_REGISTRY="docker.dev:5000" -e REGISTRY_URL="http://192.168.0.231:5000" \
-v /data/nfs/docker-registry/docker/registry/v2/:/docker-registry \
-v /usr/bin/kubectl:/usr/bin/kubectl -v /root/.kube/config:/root/.kube/config \
-p 9000:8080 -d docker-k8s