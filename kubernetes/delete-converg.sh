#!/bin/bash

# Preparing deployments on Pagoda
if [ "$1" -eq 2 ]; then
    export KUBECONFIG=~/.kube/config-pagoda
else
    export KUBECONFIG=~/.kube/config-pagoda3.yaml
fi


echo "Make sure that the KUBECONFIG file is up to date."
echo "The current KUBECONFIG file is: $KUBECONFIG"

kubectl delete -f databases --namespace=ud-evolution
kubectl delete -f conver-g --namespace=ud-evolution
kubectl delete -f dataset --namespace=ud-evolution
kubectl delete -f queries --namespace=ud-evolution
