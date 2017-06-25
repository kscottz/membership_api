#!/usr/bin/env bash
set -x
set -e

while [ $# -gt 0 ]
do
    echo "\$1=$1 \$2=$2"
    case $1 in
        -u)
            GITHUB_USER=$2
            ;;
        -p)
            GITHUB_PROJECT="$2"
            ;;
        -b)
            GITHUB_BRANCH="$2"
            ;;
        -e)
            DOTENV="$2"
    esac
    shift
    shift
done

if [ -z ${GITHUB_USER} ]; then
    GITHUB_USER=DSASanFrancisco
fi

if [ -z ${GITHUB_PROJECT} ]; then
    GITHUB_PROJECT=membership_api
fi

if [ -z ${GITHUB_BRANCH} ]; then
    GITHUB_BRANCH=master
fi

ARTIFACT_ID="$GITHUB_USER-$GITHUB_PROJECT-$GITHUB_BRANCH"
STAGE_DIR="/opt/deploy/stage/$ARTIFACT_ID"

function fetch() {
    ZIP_FILENAME="$ARTIFACT_ID.tar.gz"
    wget https://github.com/${GITHUB_USER}/${GITHUB_PROJECT}/archive/${GITHUB_BRANCH}.tar.gz -O /tmp/${ZIP_FILENAME}
    cd /tmp
    tar -xvf /tmp/${ZIP_FILENAME}
    if [ -d ${STAGE_DIR} ]; then
        rm -r ${STAGE_DIR}
    fi
    mv /tmp/${GITHUB_PROJECT}-${GITHUB_BRANCH} ${STAGE_DIR}
}

# TODO: Figure out how avoid sharing virtualenv space using docker
function venv() {
    case $1 in
        python)
            cd /opt/deploy/venv
            virtualenv ${GITHUB_PROJECT}
            ;;
        python3)
            cd /opt/deploy/venv
            virtualenv ${GITHUB_PROJECT}
            ;;
    esac
}

function upgrade() {
    case $1 in
        pip)
            source /opt/deploy/venv/${GITHUB_PROJECT}/bin/activate
            pip install -r ${STAGE_DIR}/requirements.txt
            ;;
        pip3)
            source /opt/deploy/venv/${GITHUB_PROJECT}/bin/activate
            pip3 install -r ${STAGE_DIR}/requirements.txt
            ;;
    esac
}

function install() {
    case $1 in
        env)
            cp env/${GITHUB_PROJECT}/${DOTENV}.env
            ;;
        python)
            pip install virtualenv
            venv python
            upgrade pip
            ;;
        python3)
            pip3 install virtualenv
            venv python3
            upgrade pip3
            ;;
        systemd)
            cp ${STAGE_DIR}/init/${GITHUB_PROJECT}.service /etc/systemd/system/.
            ;;
    esac
}

function push() {
    rm -rf /opt/${GITHUB_PROJECT}
    mv ${STAGE_DIR} /opt/${GITHUB_PROJECT}
}

function reload() {
    systemctl daemon-reload
    systemctl stop ${GITHUB_PROJECT}.service
    systemctl start ${GITHUB_PROJECT}.service
}

fetch
install python3
install systemd
push
reload
# TODO restart nginx?
