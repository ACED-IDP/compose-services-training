#!/bin/bash
# entrypoint script for data-portal to healthcheck sheepdog and peregrine to 
# make sure they are ready before dataportal attempts to get information from 
# them

sleep 10

until curl -f -s -o /dev/null http://sheepdog-service/v0/submission/_dictionary/_all; do
    echo "sheepdog not ready, waiting..."
    sleep 10
done

until curl -f -s -o /dev/null http://peregrine-service/v0/submission/getschema ; do
    echo "peregrine not ready, waiting..."
    sleep 10
done

echo "both services are ready"

echo START - trace data oriented setup
echo RUNNING - npm run schema
npm run schema
echo RUNNING - cat ./data/gqlSetup.js
cat ./data/gqlSetup.js
echo RUNNING - node ./data/gqlSetup.js
node ./data/gqlSetup.js
echo END - trace data oriented setup


bash ./dockerStart.sh
