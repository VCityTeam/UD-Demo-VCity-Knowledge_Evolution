#!/bin/bash

export KUBECONFIG=$1
echo "Using Pagoda $1 KUBECONFIG file"

# check if --deploy flag is part of the command parameters
if [[ "$*" == *--deploy* ]]; then
    kubectl delete -f databases --namespace=ud-evolution
    kubectl delete -f conver-g --namespace=ud-evolution

    echo "Blazegraph and ConverG components have been deleted"
fi

# check if --generation flag is part of the command parameters
if [[ "$*" == *--generation* ]]; then
    kubectl delete -f dataset/generate-dataset.yml --namespace=ud-evolution
    echo "Dataset generation has been deleted"
fi

# check if --transformation flag is part of the command parameters
if [[ "$*" == *--transformation* ]]; then
    ## Dataset transformation
    kubectl delete -f dataset/transform-dataset.yml --namespace=ud-evolution

    echo "Dataset transformation job has been deleted"
fi

# check if --import flag is part of the command parameters
if [[ "$*" == *--import* ]]; then
    ## Create the import script
    kubectl delete -f dataset/import-script-configmap.yml --namespace=ud-evolution

    ## Dataset import (relational: Postgres + ConverG)
    kubectl delete -f dataset/import-dataset-relational.yml --namespace=ud-evolution

    ## Dataset import (theoretical: Blazegraph)
    kubectl delete -f dataset/import-dataset-theoretical.yml --namespace=ud-evolution

    echo "Dataset import jobs has been deleted"
fi

# check if --query flag is part of the command parameters
if [[ "$*" == *--query* ]]; then
    # Query dataset
    ## Create query scripts
    kubectl delete -f queries/blazegraph-queries-configmap.yml --namespace=ud-evolution
    kubectl delete -f queries/converg-queries-configmap.yml --namespace=ud-evolution
    kubectl delete -f queries/query-script-configmap.yml --namespace=ud-evolution

    ## Query blazegraph
    kubectl delete -f queries/query-dataset-theoretical.yml --namespace=ud-evolution

    ## Query ConVerG
    kubectl delete -f queries/query-dataset-relational.yml --namespace=ud-evolution

    echo "Dataset query job has been deleted"
fi