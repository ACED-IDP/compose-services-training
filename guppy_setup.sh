#!/bin/bash
# Script to create and re-create es indices and setup guppy

docker exec esproxy-service curl -X DELETE http://localhost:9200/gen3.aced.*
docker compose stop guppy-service
docker compose rm -f guppy-service

./etl/tube_lite --credentials_path $1  --elastic http://localhost:9200  --batch_size 20   #  --limit 1000

docker compose up -d guppy-service
