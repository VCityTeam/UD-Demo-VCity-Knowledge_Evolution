# UD-Demo-VCity-Knowledge_Evolution
Semantic, spatial and temporal knowledge

## Context
This work is part of the larger [Virtual City Project](https://projet.liris.cnrs.fr/vcity/) of LIRIS UMR 5205 CNRS and made possible thanks to a strong collaboration between LIRIS Laboratory and Metropole of Lyon.

The goal is about thinking about the amount of knowledge developed during the last decade and use it in a multidisciplinary context for understanding city evolution and its capacity to become more sustainable and resilient.

#### Kubernetes deployment

```shell
# at the root of the project
kubectl apply -f ./kubernetes/secrets
kubectl apply -f ./kubernetes/configMap
kubectl apply -f ./kubernetes/persistentVolumeClaim
kubectl apply -f ./kubernetes/services
kubectl apply -f ./kubernetes/deployments
```

## Related Articles


## Directories
