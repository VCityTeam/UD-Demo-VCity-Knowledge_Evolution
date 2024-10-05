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

    def create_servers_containers_services(self, configurations: list[configuration], constants) -> None:
        for configuration in configurations:
            self.create_quader_container_service(configuration, constants)
            self.create_quaque_container_service(configuration, constants)

    def create_quader_container_service(self, configuration: configuration, constants) -> None:
        quader_container_name = self.layout.create_quader_container_name(configuration)
        quader_service_name = self.layout.create_quader_service_name(configuration)

        Container(
            name=quader_container_name,
            image=constants.quader,
            image_pull_policy=models.ImagePullPolicy.always,
            daemon=True,
            labels={"app": quader_container_name},
            env=[
                Env(
                    name="SPRING_DATASOURCE_URL",
                    value=self.layout.create_relational_database_url(configuration),
                ),
                Env(name="SPRING_DATASOURCE_USERNAME", value=constants.postgres_username),
                Env(name="SPRING_DATASOURCE_PASSWORD", value=constants.postgres_password),
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
                    f"   name: {quader_service_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {quader_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 8080\n"
                    "     targetPort: 8080\n")
        Resource(
            name=quader_service_name,
            action="create",
            manifest=manifest,
        )

    def create_quaque_container_service(self, configuration: configuration, constants) -> None:
        quaque_container_name = self.layout.create_quaque_container_name(configuration)
        quaque_service_name = self.layout.create_quaque_service_name(configuration)

        Container(
            name=quaque_container_name,
            image=constants.quaque,
            image_pull_policy=models.ImagePullPolicy.always,
            labels={"app": quaque_container_name},
            daemon=True,
            env=[
                Env(name="DATASOURCE_URL", value=self.layout.create_relational_database_url(configuration)),
                Env(name="DATASOURCE_USERNAME", value=constants.postgres_username),
                Env(name="DATASOURCE_PASSWORD", value=constants.postgres_password),
            ]
        )

        manifest = ("apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"   name: {quaque_service_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {quaque_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 8081\n"
                    "     targetPort: 8081\n")
        Resource(
            name=quaque_service_name,
            action="create",
            manifest=manifest,
        )