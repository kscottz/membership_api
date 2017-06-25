#!/usr/bin/env bash
set -v
set -e

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
    rm -r /opt/deploy/stage/${ARTIFACT_ID}
    mv /tmp/${PROJECT}-${BRANCH} /opt/deploy/stage/${ARTIFACT_ID}
}

function venv() {
    case $1 in
        python3)
            cd /opt/deploy/venv
            virtualenv ${PROJECT}
            ;;
    esac
}

function upgrade() {
    case $1 in
        pip)
            source /opt/deploy/venv/${PROJECT}/bin/activate
            pip install -r /opt/deploy/stage/${ARTIFACT_ID}/requirements.txt
            ;;
    esac
}

function restart() {
    systemctl stop ${PROJECT}.service
    fetch
    # TODO: Figure out how avoid sharing virtualenv space using docker
    source /opt/deploy/venv/${PROJECT}/bin/activate
    systemctl start ${PROJECT}.service
    # TODO restart nginx?
}

mkdir -p /opt/deploy/stage
#install python3
venv python3
upgrade pip
restart
