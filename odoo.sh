#!/bin/bash

set -e

VOLUMES="-v $(pwd):/usr/src"

LINKS="--link database:db"

DATA="--volumes-from purple-drill-store"

EXPOSE="-p 8069:8069"

CMD="docker run -ti --rm $LINKS $VOLUMES $DATA"

case "$1" in
    cli)
        shift
        exec $CMD purple-drill-demo -- $@
        ;;
    *)
        exec $CMD $EXPOSE purple-drill-demo $@
esac

exit 1
