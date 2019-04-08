#! /bin/bash

aws cloudformation create-stack --stack-name --region us-east-1 cfn-admin-role-stack \
  --template-url https://s3.amazonaws.com/quickstart-examples/samples/cloudformation-stack-ttl/templates/cloudformation-admin-iam.yaml \
  --capabilities "CAPABILITY_IAM" "CAPABILITY_AUTO_EXPAND" \
  --disable-rollback