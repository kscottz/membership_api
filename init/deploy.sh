#!/usr/bin/env bash
set -x
set -e

while [ $# -gt 0 ]
do
    echo "$1 $2"
    case $1 in
        -u)
            USER=$2
            ;;
        -p)
            PROJECT="$2"
            ;;
        -b)
            BRANCH="$2"
            ;;
    esac
    shift
done

if [ -z ${USER} ]; then
    USER=DSASanFrancisco
fi

if [ -z ${PROJECT} ]; then
    PROJECT=membership_api
fi

if [ -z ${BRANCH} ]; then
    BRANCH=master
fi

ARTIFACT_ID="$USER-$PROJECT-$BRANCH"
STAGE="/opt/deploy/stage/$ARTIFACT_ID"

function fetch() {
    ZIP_FILENAME="$ARTIFACT_ID.tar.gz"
    wget https://github.com/${USER}/${PROJECT}/archive/${BRANCH}.tar.gz -O /tmp/${ZIP_FILENAME}
    cd /tmp
    tar -xvf /tmp/${ZIP_FILENAME}
    rm -r ${STAGE}
    mv /tmp/${PROJECT}-${BRANCH} ${STAGE}
}

function venv() {
    case $1 in
        python)
            cd /opt/deploy/venv
            virtualenv -p python ${PROJECT}
            ;;
        python3)
            cd /opt/deploy/venv
            virtualenv -p python3 ${PROJECT}
            ;;
    esac
}

function upgrade() {
    case $1 in
        pip)
            source /opt/deploy/venv/${PROJECT}/bin/activate
            pip install -r ${STAGE}/requirements.txt
            ;;
        pip3)
            source /opt/deploy/venv/${PROJECT}/bin/activate
            pip3 install -r ${STAGE}/requirements.txt
            ;;
    esac
}

function install() {
    case $1 in
        env)
            cp ${STAGE}/.env
            ;;
        python)
            upgrade pip
            ;;
        python3)
            upgrade pip3
            ;;
        systemd)
            cp ${STAGE}/init/${PROJECT}.service /etc/systemd/system/.
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
install python3
restart
