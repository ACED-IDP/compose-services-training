export MINIO_TEST_USER=test
export MINIO_TEST_PASSWORD=testtest
export MINIO_ADMIN_USER=minioadmin
export MINIO_ADMIN_PASSWORD=minio\$1234

# setup aliases
mc alias set default http://minio-default:9000 $MINIO_ADMIN_USER $MINIO_ADMIN_PASSWORD
mc alias set ohsu http://minio-ohsu:9000 $MINIO_ADMIN_USER $MINIO_ADMIN_PASSWORD
mc alias set ucl http://minio-ucl:9000 $MINIO_ADMIN_USER $MINIO_ADMIN_PASSWORD
mc alias set manchester http://minio-manchester:9000 $MINIO_ADMIN_USER $MINIO_ADMIN_PASSWORD
mc alias set stanford http://minio-stanford:9000 $MINIO_ADMIN_USER $MINIO_ADMIN_PASSWORD

# make buckets
mc mb default/aced-default
mc mb default/aced-public
mc mb ohsu/aced-ohsu
mc mb ucl/aced-ucl
mc mb manchester/aced-manchester
mc mb stanford/aced-stanford


# add users
mc admin user add default $MINIO_TEST_USER $MINIO_TEST_PASSWORD
mc admin user add ohsu $MINIO_TEST_USER $MINIO_TEST_PASSWORD
mc admin user add ucl $MINIO_TEST_USER $MINIO_TEST_PASSWORD
mc admin user add manchester $MINIO_TEST_USER $MINIO_TEST_PASSWORD
mc admin user add stanford $MINIO_TEST_USER $MINIO_TEST_PASSWORD

# add policies
mc admin policy set default readwrite user=$MINIO_TEST_USER
mc admin policy set ohsu readwrite user=$MINIO_TEST_USER
mc admin policy set ucl readwrite user=$MINIO_TEST_USER
mc admin policy set manchester readwrite user=$MINIO_TEST_USER
mc admin policy set stanford readwrite user=$MINIO_TEST_USER
# public bucket
mc policy set public default/aced-public

# when objects added to bucket, call webhook (see minio-webhook/ for example)
mc event add default/aced-default arn:minio:sqs::PRIMARY:webhook
mc event add ohsu/aced-ohsu arn:minio:sqs::PRIMARY:webhook
mc event add ucl/aced-ucl arn:minio:sqs::PRIMARY:webhook
mc event add manchester/aced-manchester arn:minio:sqs::PRIMARY:webhook
mc event add stanford/aced-stanford arn:minio:sqs::PRIMARY:webhook

