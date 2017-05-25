#!/bin/bash
set -e

echo "Logging in"
neres --email ${NERES_EMAIL} --password ${NERES_PASSWORD} login

echo "List accounts"
neres list-accounts

echo "List locations"
neres list-locations

echo "Add monitor"
ID=$(neres add-monitor `date "+%Y%m%H%M%s"` http://www.example.com --raw | jq --raw-output '.id')

echo "Get monitor"
neres get-monitor ${ID}

echo "Update monitor"
neres update-monitor ${ID} --name `date "+%Y%m%H%M%s"` --frequency 1440

echo "List monitors"
neres list-monitors| grep ${ID}

echo "Get state"
neres get-state > state.yml

echo "Update state"
sed -i -e 's/frequency: 1440/frequency: 720/g' state.yml
neres update-from-statefile state.yml
neres update-from-statefile state.yml --apply
neres get-monitor ${ID} --raw | jq .frequency | grep 720

echo "Delete monitor"
neres delete-monitor ${ID} --confirm ${ID}
