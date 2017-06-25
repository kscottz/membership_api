#!/usr/bin/env bash

USER="$1"
PROJECT="$2"
BRANCH="$3"
ARTIFACT_ID="${USER}-${PROJECT}-${BRANCH}"

if [ -z ${USER} ]; then
    USER=DSASanFrancisco
fi

if [ -z ${PROJECT} ]; then
    PROJECT=membership_api
fi

if [ -z ${BRANCH} ]; then
    BRANCH=master
fi

function fetch() {
    ZIP_FILENAME="$ARTIFACT_ID.tar.gz"
    wget https://github.com/${USER}/${PROJECT}/archive/${BRANCH}.tar.gz -O /tmp/${ZIP_FILENAME}
    cd /tmp
    tar -xvf /tmp/${ZIP_FILENAME}
    mv /tmp/${PROJECT}-${BRANCH} /opt/deploy/stage/${ARTIFACT_ID}
}

function restart() {
    systemctl stop ${PROJECT}.service
    fetch
    # TODO: figure out how to standardize this
    source /opt/deploy/venv/${PROJECT}/bin/activate
    pip install -r /opt/deploy/${ARTIFACT_ID}/requirements.txt
    systemctl start ${PROJECT}.service
    # TODO restart nginx?
}

mkdir -p /opt/deploy/stage
restart
