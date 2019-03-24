#! /bin/bash

DIR=$(realpath $(dirname run.sh ))
APP_NAME=$(basename ${DIR})

if [[ -z $(docker images -q dlmbot) ]]; then
    echo "Building docker image..."
    docker build -t ${APP_NAME} ${DIR}
fi

docker run -it --rm --volume ${DIR}:/app ${APP_NAME}