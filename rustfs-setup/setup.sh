#!/bin/sh

mc alias set rustfs $BUCKET_HOST $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY
mc ls rustfs
mc mb -p rustfs/$BUCKET_NAME
mc anonymous set download rustfs/$BUCKET_NAME
