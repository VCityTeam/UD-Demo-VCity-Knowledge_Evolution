from hera.workflows import (
    ConfigMapEnvFrom,
    Container,
    Resource,
    ConfigMapEnvFrom,
    Env,
    models
)
from experiment_layout import layout
from environment import environment
from configuration import configuration

class databases:
    def __init__(self, layout: layout, environment: environment):
        self.layout = layout
        self.environment = environment

    def generate_databases_configurations(self, parameters: object) -> list:
        from itertools import product

        # generate the instances: it has to be all combinations of the arguments
        configurations = list(product(
            parameters["versions"],
            parameters["products"],
            parameters["steps"],
            parameters["variabilities"]
        ))

        return [
                configuration(
                    version,
                    product,
                    step,
                    variability
                )
            for (version, product, step, variability) in configurations
        ]


    def create_postgres_container_service(self, configuration: configuration, constants) -> None:
        postgres_container_name = self.layout.create_postgres_container_name(configuration)
        Container(
            name=postgres_container_name,
            image=constants.postgres,
            image_pull_policy=models.ImagePullPolicy.always,
            daemon=True,
            env=[
                Env(
                    name="POSTGRES_DB",
                    value=self.layout.create_database_identifier(configuration),
                ),
                Env(name="POSTGRES_USER", value=constants.postgres_username),
                Env(name="POSTGRES_PASSWORD", value=constants.postgres_password),
                Env(name="PGDATA", value=self.environment.database_data(configuration)),
            ],
            env_from=[
                # Assumes the corresponding config map is defined at k8s level
                ConfigMapEnvFrom(
                    name=self.environment.cluster.proxy_configmap,
                    optional=False,
                )
            ],
        )

        manifest = ("apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"   name: {postgres_container_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {postgres_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 5432\n"
                    "     targetPort: 5432\n")

        Resource(
            name=f'{postgres_container_name}-service',
            action="create",
            manifest=manifest,
        )

    def create_blazegraph_container_service(self, configuration: configuration, constants) -> None:
        blazegraph_container_name = self.layout.create_blazegraph_container_name(configuration)

        Container(
            name=blazegraph_container_name,
            image=constants.blazegraph,
            image_pull_policy=models.ImagePullPolicy.always,
            daemon=True,
            env=[
                Env(
                    name="BLAZEGRAPH_QUADS",
                    value="true",
                ),
                Env(name="BLAZEGRAPH_TIMEOUT", value="180000"),
                Env(name="BLAZEGRAPH_MEMORY", value="32G"),
            ]
        )

        manifest = ("apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"   name: {blazegraph_container_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {blazegraph_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 9999\n"
                    "     targetPort: 8080\n")
        Resource(
            name=f'{blazegraph_container_name}-service',
            action="create",
            manifest=manifest,
        )

    def create_dbs_containers_services(self, configurations: list, constants) -> None:
        for configuration in configurations:
            self.create_postgres_container_service(configuration, constants)
            self.create_blazegraph_container_service(configuration, constants)