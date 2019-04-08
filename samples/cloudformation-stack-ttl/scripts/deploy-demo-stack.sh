#! /bin/bash

aws cloudformation create-stack --stack-name --region us-east-1 demo-stack-ttl \
  --template-url https://s3.amazonaws.com/quickstart-examples/samples/cloudformation-stack-ttl/templates/demo-stack-ttl.yaml \
  --capabilities "CAPABILITY_IAM" "CAPABILITY_AUTO_EXPAND" \
  --role-arn "<ADD_CLOUDFORMATION_SERVICE_ROLE_ARN_HERE>" \
  --disable-rollback