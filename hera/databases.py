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
from itertools import product

class databases:
    def __init__(self, layout: layout, environment: environment):
        self.layout = layout
        self.environment = environment

    def generate_databases_configurations(self, parameters: object) -> list:
        """
        Generates a list of database configurations based on the provided parameters.

        Args:
            parameters (object): An object containing the following keys:
                - "versions" (list): A list of version identifiers.
                - "products" (list): A list of product identifiers.
                - "steps" (list): A list of step identifiers.
                - "variabilities" (list): A list of variability identifiers.

        Returns:
            list: A list of configuration objects, each representing a unique combination
                  of version, product, step, and variability.
        """
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
        """
        Creates a PostgreSQL container service within a Kubernetes cluster.
        This method sets up a PostgreSQL container with the specified configuration and constants.
        It defines the container's environment variables, image, and other properties, and then
        creates a corresponding Kubernetes service manifest to expose the container.
        Args:
            configuration (configuration): The configuration object containing settings for the PostgreSQL container.
            constants: An object containing constant values such as image name, username, and password.
        Returns:
            None
        """
        postgres_container_name = self.layout.create_postgres_container_name(configuration)
        postgres_service_name = self.layout.create_postgres_service_name(configuration)
        Container(
            name=postgres_container_name,
            image=constants.postgres,
            image_pull_policy=models.ImagePullPolicy.always,
            daemon=True,
            labels={"app": postgres_container_name},
            env=[
                Env(
                    name="POSTGRES_DB",
                    value=self.layout.create_database_identifier(configuration),
                ),
                Env(name="POSTGRES_USER", value=constants.postgres_username),
                Env(name="POSTGRES_PASSWORD", value=constants.postgres_password),
                Env(name="PGDATA", value=self.environment.database_data(configuration)),
            ]
        )

        manifest = ("apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"   name: {postgres_service_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {postgres_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 5432\n"
                    "     targetPort: 5432\n")

        Resource(
            name=postgres_service_name,
            action="create",
            manifest=manifest,
        )

    def create_blazegraph_container_service(self, configuration: configuration, constants) -> None:
        """
        Creates a Blazegraph container service.

        This method sets up a Blazegraph container with the specified configuration and constants.
        It configures the container with environment variables and creates a Kubernetes service
        manifest to expose the container.

        Args:
            configuration (configuration): The configuration object containing settings for the container.
            constants: An object containing constant values, including the Blazegraph image.

        Returns:
            None
        """
        blazegraph_container_name = self.layout.create_blazegraph_container_name(configuration)
        blazegraph_service_name = self.layout.create_blazegraph_service_name(configuration)

        Container(
            name=blazegraph_container_name,
            image=constants.blazegraph,
            image_pull_policy=models.ImagePullPolicy.always,
            labels={"app": blazegraph_container_name},
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
                    f"   name: {blazegraph_service_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {blazegraph_container_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    "   - port: 9999\n"
                    "     targetPort: 8080\n")
        Resource(
            name=blazegraph_service_name,
            action="create",
            manifest=manifest,
        )

    def create_dbs_containers_services(self, configurations: list, constants) -> None:
        """
        Creates database containers and services for the given configurations.

        This method iterates over a list of configurations and creates PostgreSQL
        and Blazegraph container services for each configuration.

        Args:
            configurations (list): A list of configuration objects.
            constants: A set of constants used for creating the container services.

        Returns:
            None
        """
        for configuration in configurations:
            self.create_postgres_container_service(configuration, constants)
            self.create_blazegraph_container_service(configuration, constants)