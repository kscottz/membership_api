#!/usr/bin/env bash

set -x
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
if [ ! -d "$DIR" ]; then
	echo "Not a directory: '$DIR'"
	exit 1
fi

pushd ${DIR}

function show_help() {
	echo "Enter a project name to build the docker project in that directory."
}

# Show help if only 1 arg
if [ "$1" == "" ]; then
	show_help
	exit 0
else
	while [ $# -gt 0 ]
	do
		# Parse command or option
		case $1 in
			--help)
				CMD="help"
				;;
			*)
				CMD="build"
				;;
		esac

		# Process command
		case $CMD in
			build)
				APP="$DIR/docker/$1"
				INIT="$APP/init"
				STAGE="$APP/stage"
				if [ -d "$STAGE" ]; then
					rm -r "$STAGE"
				fi
				mkdir -p "$STAGE"
				cp -r "$INIT" "$STAGE/init"
				# Copy selective files over based on project
				case $1 in
					api)
						cp -r requirements.txt flask_app.py config membership "$STAGE/."
						;;
					*)
						"Unrecognized app name '$ARG'"
						exit 1
				esac
				docker build "$APP" -t membership_api
				;;
			help)
				show_help
				exit 0
				;;
		esac
		shift
	done
fi

popd
