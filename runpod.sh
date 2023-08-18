#!/bin/bash

Help() {
    echo "Usage:   $0 <EARFCN>"
    echo "Example: $0 700"
    echo
    exit 1
}

# Cheking arguments
if [ "$#" -ne 1 ]; then
    Help
fi

podman run --name ng-scope -ti --privileged --rm -v $(pwd):/ng-scope/build/ngscope/src/logs/ docker.io/j0lama/ng-scope:latest ./start.sh 1 $1