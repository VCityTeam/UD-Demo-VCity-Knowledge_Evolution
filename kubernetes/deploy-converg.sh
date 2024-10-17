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

# Check if there are at least 2 parameters
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <KUBECONFIG_FILE> --deploy --ingresses --generation --transformation --import --query"
    echo "Example: $0 ~/.kube/config-pagoda3.yaml --deploy --ingresses --generation --transformation --import --query"
    exit 1
fi

export KUBECONFIG=$1
echo "Using Pagoda $1 KUBECONFIG file"

# check if --deploy flag is part of the command parameters
if [[ "$*" == *--deploy* ]]; then
    # Deploying the databases (Blazegraph and Postgres) and the Converg components
    kubectl apply -f databases --namespace=ud-evolution
    kubectl apply -f conver-g --namespace=ud-evolution

    # Handmade workflow
    kubectl apply -f dataset/dataset-pvc.yml --namespace=ud-evolution

    echo "Blazegraph and ConverG components have been deployed"
fi

# check if --ingresses flag is part of the command parameters
if [[ "$*" == *--ingresses* ]]; then
    # Deploying the ingresses
    kubectl apply -f ingresses --namespace=ud-evolution

    echo "All ingresses have been deployed"
fi

# check if --generation flag is part of the command parameters
if [[ "$*" == *--generation* ]]; then
    ## Dataset generation
    kubectl apply -f dataset/generate-dataset.yml --namespace=ud-evolution
    execute_job_and_wait dataset-generation-job

    echo "Dataset has been generated"
fi

# check if --transformation flag is part of the command parameters
if [[ "$*" == *--transformation* ]]; then
    ## Dataset transformation
    kubectl apply -f dataset/transform-dataset.yml --namespace=ud-evolution
    execute_job_and_wait dataset-transformer-job

    echo "Dataset has been transformed"
fi

# check if --import flag is part of the command parameters
if [[ "$*" == *--import* ]]; then
    ## Create the import script
    kubectl apply -f dataset/import-script-configmap.yml --namespace=ud-evolution

    ## Dataset import (relational: Postgres + ConverG)
    kubectl apply -f dataset/import-dataset-relational.yml --namespace=ud-evolution
    ## Dataset import (theoretical: Blazegraph)
    kubectl apply -f dataset/import-dataset-theoretical.yml --namespace=ud-evolution

    execute_job_and_wait relational-dataset-importer-job
    execute_job_and_wait theoretical-dataset-importer-job

    ## Dataset import (relational: Postgres + ConverG)
    kubectl apply -f dataset/import-dataset-relational-alt.yml --namespace=ud-evolution
    ## Dataset import (theoretical: Blazegraph)
    kubectl apply -f dataset/import-dataset-theoretical-alt.yml --namespace=ud-evolution

    execute_job_and_wait relational-dataset-importer-job-alt
    execute_job_and_wait theoretical-dataset-importer-job-alt

    echo "Dataset has been imported"
fi

# check if --query flag is part of the command parameters
if [[ "$*" == *--query* ]]; then
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

    echo "Dataset has been queried"
fi
