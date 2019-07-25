#!/usr/bin/env bash
export KEY_PAIR_NAME=cikey
aws cloudformation --region us-east-2 create-stack --stack-name ssm-ssh-demo \
  --template-url https://aws-quickstart.s3.amazonaws.com/quickstart-examples/samples/session-manager-ssh/session-manager-ssh-example.yaml \
  --parameters ParameterKey=KeyPairName,ParameterValue=${KEY_PAIR_NAME} ParameterKey=AvailabilityZones,ParameterValue=us-east-2a\\,us-east-2b \
  --capabilities "CAPABILITY_IAM" --disable-rollback
