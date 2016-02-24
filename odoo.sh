#!/bin/bash

set -e

VOLUMES="-v $(pwd):/usr/src"

LINKS="--link database:db"

DATA="--volumes-from purple-screwdriver-store"

EXPOSE="-p 8069:8069"

CMD="docker run -ti --rm $LINKS $VOLUMES $DATA"


case "$1" in
    cli)
        shift
        exec $CMD purple-screwdriver -- $@
        ;;
    screwdriver)
        shift
        exec $CMD purple-screwdriver -- screwdriver $@
        ;;
    *)
        exec $CMD $EXPOSE purple-screwdriver $@
esac

exit 1
