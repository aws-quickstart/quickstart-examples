#!/bin/bash
# Install kubectl

# we are installing the current version if you are on an older cluster you might need to change this.
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
# Install kubectl
install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

#============= INSERT YOUR PREWORK STEPS HERE ====================#
# We will create a simple script the point of the blog is to show that you CAN run pre-work on the cluster via CloudFormation
# so we are less concerned with the content of this script.

# there are much better ways to manage secrets ;)
kubectl create secret generic db-user-pass \
  --from-literal=username=devuser \
  --from-literal=password='S!B\*d$zDsb=' \
  -- namespace $KUBE_NAMESPACE
kubectl describe secrets/db-user-pass