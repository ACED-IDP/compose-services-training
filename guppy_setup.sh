#!/bin/bash
# Script to create and re-create es indices and setup guppy

docker exec esproxy-service curl -X DELETE http://localhost:9200/gen3.aced.*
docker compose stop guppy-service
docker compose rm -f guppy-service

# start two processes one for observation and one for file, run them in parallel at a higher 'niceness' level
echo -e observation"\n"file  | nice -n 10 xargs -L 1 -P 2 nice -n 10 ./etl/tube_lite --credentials_path $1  --elastic http://localhost:9200  --batch_size 20  --entity

docker compose up -d guppy-service
