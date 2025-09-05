# UD-Demo-VCity-Knowledge_Evolution

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

## Related Articles

- BDA 2023: [Graph versioning for evolving urban data](https://hal.science/hal-04257528)
- BDA 2024 [ConVer-G: Concurrent versioning of knowledge graphs](https://hal.science/hal-04690144)
