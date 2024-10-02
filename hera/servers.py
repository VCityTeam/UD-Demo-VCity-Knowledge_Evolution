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

class servers:
    def __init__(self, layout: layout, environment: environment):
        self.layout = layout
        self.environment = environment

    def create_servers_containers(self, configurations: list[configuration], constants) -> None:
        for configuration in configurations:
            quader_container_name = self.layout.create_quader_container_name(configuration)
            quaque_container_name = self.layout.create_quaque_container_name(configuration)

            Container(
                name=quader_container_name,
                image=constants.quader,
                image_pull_policy=models.ImagePullPolicy.always,
                daemon=True,
                env=[
                    Env(
                        name="SPRING_DATASOURCE_URL",
                        value=self.layout.create_relational_database_url(configuration),
                    ),
                    Env(name="SPRING_DATASOURCE_PASSWORD", value="password"), # FIXME: Use a secret
                    Env(name="SPRING_DATASOURCE_USERNAME", value="user"), # FIXME: Use a secret
                ],
                env_from=[
                    # Assumes the corresponding config map is defined at k8s level
                    ConfigMapEnvFrom(
                        name=self.environment.cluster.proxy_configmap,
                        optional=False,
                    )
                ],
            )
            Container(
                name=quaque_container_name,
                image=constants.quaque,
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
