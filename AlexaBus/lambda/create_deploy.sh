#!/bin/bash
rm deploy.zip

pushd awslambda-psycopg2
zip -r ../deploy.zip psycopg2
popd
zip -ur deploy.zip db_handler.py lambda_function.py SQL
pushd ../
zip -u lambda/deploy.zip config.py
popd