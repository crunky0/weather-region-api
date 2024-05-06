#!/bin/bash

export DB_API_KEY="MhQa5eirWEp18p6G4boIJ4zTXzQgsepaGIHrf55zdiZ7imci4RGoYTWSete1Gm8I"
export WEATHER_API_KEY="b9f8e0261de93e161fd8a9bd5edbc713"

python restapi.py --weather-api-key $WEATHER_API_KEY --db-api-key $DB_API_KEY
