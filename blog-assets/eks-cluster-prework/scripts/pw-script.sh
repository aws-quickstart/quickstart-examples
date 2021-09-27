#!/bin/bash
# Install kubectl
yum install -y unzip

# TODO: Make this generic based on the EKS Version
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.16.8/2020-04-16/bin/linux/amd64/kubectl
chmod +x ./kubectl

#============= INSERT YOUR PREWORK STEPS HERE ====================#
# Confirm VNI version (Current is 1.9.0) - we could just assume this since it is a new cluster
kubectl describe daemonset aws-node --namespace kube-system | grep Image | cut -d "/" -f 2 > /tmp/foo.txt
# TODO: add to a kubernetes secret we output into the CloudFormation template 

# Set AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG to True
kubectl set env daemonset aws-node -n kube-system AWS_VPC_K8S_CNI_CUSTOM_NETWORK_CFG=true

# Add additional steps below 
