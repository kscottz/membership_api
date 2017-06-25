#!/usr/bin/env bash

USER="$1"
if [ -z ${USER} ]; then
    USER=DSASanFrancisco
fi

PROJECT="$2"
if [ -z ${PROJECT} ]; then
    PROJECT=membership_api
fi

BRANCH="$3"
if [ -z ${BRANCH} ]; then
    BRANCH=master
fi

ARTIFACT_ID="${USER}-${PROJECT}-${BRANCH}"

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
    # TODO: Figure out how avoid sharing virtualenv space using docker
    source /opt/deploy/venv/${PROJECT}/bin/activate
    pip install -r /opt/deploy/stage/${ARTIFACT_ID}/requirements.txt
    systemctl start ${PROJECT}.service
    # TODO restart nginx?
}

mkdir -p /opt/deploy/stage
restart
