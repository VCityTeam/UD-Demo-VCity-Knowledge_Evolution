# UD-Demo-VCity-Knowledge_Evolution
Semantic, spatial and temporal knowledge

## Context
This work is part of the larger [Virtual City Project](https://projet.liris.cnrs.fr/vcity/) of LIRIS UMR 5205 CNRS and made possible thanks to a strong collaboration between LIRIS Laboratory and Metropole of Lyon.

The goal is about thinking about the amount of knowledge developed during the last decade and use it in a multidisciplinary context for understanding city evolution and its capacity to become more sustainable and resilient.

## Linked components

- [ConVer-G](https://github.com/VCityTeam/ConVer-G)
- [PostgreSQL](https://www.postgresql.org/docs/16/index.html)

### Kubernetes deployment
#### Deploy

Quickstart:

```shell
# inside the kubernetes folder
# ./deploy-converg.sh <k8s config file path> <?args>

./deploy-converg.sh ~/.kube/config-pagoda3.yaml --deploy --generation --transformation --import --query
```

Args:
- `--deploy`: deploy the Blazegraph and ConVer-G components
- `--generation`: deploy the dataset generation job
- `--transformation`: deploy the dataset transformation job
- `--import`: deploy the dataset import job
- `--query`: deploy the dataset query job

Details:
```shell
export KUBE_DOCKER_REGISTRY=<your docker registry>
export KUBECONFIG=<your kubernetes config file>

# at the root of the project
kubectl apply -f ./kubernetes/conver-g
kubectl apply -f ./kubernetes/databases
```

#### Stop

Quickstart:

```shell
# inside the kubernetes folder
# ./delete-converg.sh <k8s config file path> <?args>

./delete-converg.sh ~/.kube/config-pagoda3.yaml --deploy --generation --transformation --import --query
```

Args:
- `--deploy`: deploy the Blazegraph and ConVer-G components
- `--generation`: deploy the dataset generation job
- `--transformation`: deploy the dataset transformation job
- `--import`: deploy the dataset import job
- `--query`: deploy the dataset query job

Details:

```shell
# at the root of the project
kubectl delete -f ./kubernetes/conver-g
kubectl delete -f ./kubernetes/databases
```

### Minikube pods port forwarding

```shell
# Get access to the ud-quads-importer pod (http://localhost:8080)
kubectl port-forward services/ud-quads-importer 8080:8080

# Get access to the postgres pod (localhost:5432)
kubectl port-forward services/postgres 5432:5432
```

### Hera workflow
    
```shell
# set the environment variables
export POSTGRES_USER="<username>" 
export POSTGRES_PASSWORD="<password>"

# print the help
python experiment.py --help

# execute the experiment
python experiment.py --versions 1 10 100 1000 --products 5 20 80 350 --steps 1 5 10 50 --variabilities 0 1 10 100
```

```mermaid
flowchart TD
%% Nodes
    A("<a rel="noopener" href="https://github.com/argoproj-labs/hera" target="_blank">Hera workflow</a>")
    B("<a rel="noopener" href="https://github.com/argoproj/argo-workflows" target="_blank">Argo workflows Server</a>")
    C("Argo workflows Controller")
    D((iterator))
    subgraph Experiment[<a rel="noopener" href="https://github.com/VCityTeam/ConVer-G" target="_blank">ConVer-G</a>]
        E(<a rel="noopener" href="https://hub.docker.com/r/vcity/quads-loader" target="_blank">Quads Loader</a>)
        I(<a rel="noopener" href="https://hub.docker.com/r/vcity/quads-query" target="_blank">Quads Query</a>)
        
        F(<a rel="noopener" href="https://github.com/VCityTeam/BSBM" target="_blank">Generate dataset</a>)
        subgraph Transform[<a rel="noopener" href="https://hub.docker.com/r/vcity/quads-creator" target="_blank">Transform dataset</a>]
            H1(Relational transformation)
            H2(Theoretical transformation)
        end
        G(<a rel="noopener" href="https://hub.docker.com/r/vcity/blazegraph-cors" target="_blank">Blazegraph</a>)

        J(Query backends)
    end

%% Edge connections between nodes
    A --> |submit| B --> C --> D
    D --> |starts with params| E & G & F & I
    D --> |launches queries| J
    F --> H1 & H2 
    H1 --> |Sends dataset| E
    H2 --> |Sends dataset| G
    J --> |Sends query| G & I
```

## Related Articles

- BDA 2023: [Graph versioning for evolving urban data](https://hal.science/hal-04257528)
- BDA 2024 [ConVer-G: Concurrent versioning of knowledge graphs](https://hal.science/hal-04690144)