#!/bin/bash

execute_job_and_wait() {
    job_name=$1
    job_completed=false
    while ! $job_completed; do
        kubectl wait --for=condition=complete job/$job_name --timeout=30s --namespace=ud-evolution
        if [[ $? -eq 0 ]]; then
            echo "Job $job_name completed successfully"
            job_completed=true
        fi
        echo "Waiting for job $job_name to complete"
    done
}

# Preparing deployments on Pagoda
export KUBECONFIG=~/.kube/config-pagoda3.yaml

echo "Make sure that the KUBECONFIG file is up to date."
echo "The current KUBECONFIG file is: $KUBECONFIG"

kubectl apply -f databases --namespace=ud-evolution
kubectl apply -f conver-g --namespace=ud-evolution

# Handmade workflow
kubectl apply -f dataset/dataset-pvc.yml --namespace=ud-evolution

echo "Dataset is ready to be generated"

kubectl apply -f dataset/generate-dataset.yml --namespace=ud-evolution
execute_job_and_wait dataset-generation-job

echo "Dataset is ready to be transformed"

kubectl apply -f dataset/transform-dataset.yml --namespace=ud-evolution
execute_job_and_wait dataset-transformer-job

echo "Dataset is ready to be imported"

kubectl apply -f dataset/import-script-configmap.yml --namespace=ud-evolution
kubectl apply -f dataset/import-dataset.yml --namespace=ud-evolution
execute_job_and_wait dataset-importer-job

echo "Dataset is ready to be used"