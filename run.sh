#!/bin/bash
pipenv run app &
APP_ID=$!
cd ./toio-exec/; yarn run exec
kill $APP_ID
