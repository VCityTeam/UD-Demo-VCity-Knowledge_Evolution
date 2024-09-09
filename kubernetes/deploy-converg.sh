#!/bin/bash

execute_job_and_wait() {
    job_name=$1
    job_completed=false
    while ! $job_completed; do
        kubectl wait --for=condition=complete job/$job_name --timeout=120s --namespace=ud-evolution
        if [[ $? -eq 0 ]]; then
            echo "Job $job_name completed successfully"
            job_completed=true
        fi
        echo "Waiting for job $job_name to complete"
    done
}

# Preparing deployments on Pagoda
if [ "$1" -eq 2 ]; then
    export KUBECONFIG=~/.kube/config-pagoda
else
    export KUBECONFIG=~/.kube/config-pagoda3.yaml
fi


echo "Make sure that the KUBECONFIG file is up to date."
echo "The current KUBECONFIG file is: $KUBECONFIG"

# Deploying the databases (Blazegraph and Postgres) and the Converg components
kubectl apply -f databases --namespace=ud-evolution
kubectl apply -f conver-g --namespace=ud-evolution

# Handmade workflow
kubectl apply -f dataset/dataset-pvc.yml --namespace=ud-evolution

echo "Dataset is ready to be generated"

## Dataset generation
kubectl apply -f dataset/generate-dataset.yml --namespace=ud-evolution
execute_job_and_wait dataset-generation-job

echo "Dataset is ready to be transformed"

## Dataset transformation
kubectl apply -f dataset/transform-dataset.yml --namespace=ud-evolution
execute_job_and_wait dataset-transformer-job

echo "Dataset is ready to be imported"

## Create the import script
kubectl apply -f dataset/import-script-configmap.yml --namespace=ud-evolution

## Dataset import (relational: Postgres + ConverG)
kubectl apply -f dataset/import-dataset-relational.yml --namespace=ud-evolution
execute_job_and_wait relational-dataset-importer-job

## Dataset import (theoretical: Blazegraph)
kubectl apply -f dataset/import-dataset-theoretical.yml --namespace=ud-evolution
execute_job_and_wait theoretical-dataset-importer-job

# Query dataset
## Create query scripts
kubectl apply -f queries/blazegraph-queries-configmap.yml --namespace=ud-evolution
kubectl apply -f queries/converg-queries-configmap.yml --namespace=ud-evolution
kubectl apply -f queries/query-script-configmap.yml --namespace=ud-evolution

## Query blazegraph
kubectl apply -f queries/query-dataset-theoretical.yml --namespace=ud-evolution
execute_job_and_wait theoretical-dataset-query-job

## Query ConVerG
kubectl apply -f queries/query-dataset-relational.yml --namespace=ud-evolution
execute_job_and_wait relational-dataset-query-job
