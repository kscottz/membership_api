#!/usr/bin/env bash

USER="$1"
PROJECT="$2"
BRANCH="$3"

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
    ZIP_FILENAME="${USER}-${PROJECT}-${BRANCH}.tar.gz"
    wget https://github.com/${USER}/${PROJECT}/archive/${BRANCH}.tar.gz -O /tmp/${ZIP_FILENAME}
    tar -xvf /tmp/${ZIP_FILENAME}
    mv /tmp/${PROJECT}-${BRANCH} /opt/deploy/${PROJECT}
}

function restart() {
    systemctl stop membership_api.service
    fetch
    source /opt/deploy/venv/membership_api/bin/activate
    pip install -r /opt/deploy/membership_api/requirements.txt
    systemctl start membership_api.service
    # TODO restart nginx?
}

restart
