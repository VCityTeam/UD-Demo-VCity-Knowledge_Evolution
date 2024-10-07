from hera.workflows import (
    Container,
    models,
    ExistingVolume,
    Volume,
    Resource
)
from hera.workflows.models import VolumeMount
from experiment_layout import layout
from environment import environment
from configuration import configuration
from itertools import product

class datasets:
    def __init__(self, layout: layout, environment: environment):
        self.layout = layout
        self.environment = environment

    def create_datasets_volumes(self, configurations: list[configuration]) -> None:
        """
        Creates PersistentVolumeClaim resources for each configuration provided.
        This method iterates over a list of configurations and generates a 
        PersistentVolumeClaim manifest for each one. The manifest is then used 
        to create a resource with the specified name, action, and owner reference.
        Args:
            configurations (list[configuration]): A list of configuration objects 
            that contain the necessary information to create the PersistentVolumeClaim 
            resources.
        Returns:
            None
        """
        for configuration in configurations:
            manifest = ("apiVersion: v1\n"
                "kind: PersistentVolumeClaim\n"
                "metadata:\n"
                f"   name: {self.environment.compute_dataset_volume_name(configuration)}\n"
                "spec:\n"
                "   accessModes:\n"
                "       - ReadWriteOnce\n"
                "   resources:\n"
                "       requests:\n"
                f"          storage: {self.environment.compute_dataset_volume_size(configuration)}\n")
            Resource(
                name=self.environment.compute_dataset_volume_name(configuration),
                action="create",
                set_owner_reference=True,
                manifest=manifest
            )

    def create_datasets_containers(self, configurations: list[configuration], constants) -> None:        
        """
        Creates dataset containers based on the provided configurations.
        This method iterates over a list of configuration objects and creates a container for each configuration.
        Each container is configured with a specific volume mount and image, and is set up to generate data 
        based on the configuration parameters.
        Args:
            configurations (list[configuration]): A list of configuration objects that define the parameters 
                              for each dataset container.
            constants: An object containing constant values, including the image to be used for the containers.
        Returns:
            None
        """
        for configuration in configurations:
            bsbm_container_name = self.layout.create_bsbm_container_name(configuration)

            volume_mount = ExistingVolume(
                name=self.environment.compute_dataset_volume_name(configuration),
                claim_name=self.environment.compute_dataset_volume_name(configuration),
                mount_path=f"/app/data",
            )

            Container(
                name=bsbm_container_name,
                image=constants.bsbm,
                image_pull_policy=models.ImagePullPolicy.always,
                args=["generate-n", configuration.version, configuration.product, configuration.step, configuration.variability],
                volumes=[volume_mount]
            )

    def generate_datasets_configurations(self, arguments: object) -> list:
        """
        Generate dataset configurations based on the provided arguments.
        This method takes an object containing various arguments and generates a list of dataset configurations.
        The configurations are created by taking the Cartesian product of the provided versions, products, steps, 
        and variabilities. Note that the configurations set of the datasets are a subset of server configurations.
        Args:
            arguments (object): An object containing the following keys:
                - versions (list): A list of version numbers. (here, only the maximum version is considered)
                - products (list): A list of product names.
                - steps (list): A list of steps.
                - variabilities (list): A list of variabilities.
        Returns:
            list: A list of dataset configurations, where each configuration is represented as a tuple 
                  (version, product, step, variability).
        """
        versions = [max(arguments["versions"])]

        configurations = list(product(
            versions,
            arguments["products"],
            arguments["steps"],
            arguments["variabilities"]
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
    
    def create_datasets_transformers(self, configurations: list[configuration], constants) -> None:        
        """
        Creates dataset transformers for each configuration provided.
        This method iterates over a list of configurations and creates two types of dataset transformers 
        ('relational' and 'theoretical') for each configuration using the provided constants.
        Args:
            configurations (list[configuration]): A list of configuration objects to process.
            constants: A set of constants used in the creation of dataset transformers.
        Returns:
            None
        """
        for configuration in configurations:
            self.create_typed_dataset_transformer(configuration, constants, 'relational')
            self.create_typed_dataset_transformer(configuration, constants, 'theoretical')
    
    def create_typed_dataset_transformer(self, configuration: configuration, constants, type: str) -> None:
        """
        Creates a typed dataset transformer container based on the provided configuration and type.
        Args:
            configuration (configuration): The configuration object containing necessary settings.
            constants: A module or object containing constant values used in the container creation.
            type (str): The type of dataset transformer to create. Must be either "relational" or "theoretical".
        Raises:
            Exception: If the provided type is not "relational" or "theoretical".
        Returns:
            None
        """
        if (type != "relational" and type != "theoretical"):
            raise Exception(f"Unknown dataset type: {type}")

        typed_transformer_container_name = self.layout.create_typed_transformer_container_name(configuration, type)

        volume_mount = ExistingVolume(
            name=self.environment.compute_dataset_volume_name(configuration),
            claim_name=self.environment.compute_dataset_volume_name(configuration),
            mount_path=f"/app/data",
        )

        Container(
            name=typed_transformer_container_name,
            image=constants.quads_transformer,
            image_pull_policy=models.ImagePullPolicy.always,
            args=[
                f"/app/data/{type}",
                f"/app/data",
                "*",
                type,
                "BSBM"
            ],
            volumes=[volume_mount]
        )

    def create_datasets_importers(self, configurations: list[configuration], constants) -> None:
        for configuration in configurations:
            self.create_typed_dataset_importer(configuration, constants, 'relational')
            self.create_typed_dataset_importer(configuration, constants, 'theoretical')

    def create_typed_dataset_importer(self, configuration: configuration, constants, type: str) -> None:
        if (type != "relational" and type != "theoretical"):
            raise Exception(f"Unknown dataset type: {type}")

        typed_importer_container_name = self.layout.create_typed_importer_container_name(configuration, type)

        existing_volume = ExistingVolume(
            name=self.environment.compute_dataset_volume_name(configuration),
            claim_name=self.environment.compute_dataset_volume_name(configuration),
            mount_path=f"/app/data",
        )
        configmap_volume = Volume(
            name=self.environment.compute_configmap_volume_name(configuration, type),
            configmap_name=self.environment.cluster.importers_configmap,
        )

        Container(
            name=typed_importer_container_name,
            image=constants.ubuntu,
            image_pull_policy=models.ImagePullPolicy.always,
            command=["/bin/bash", "-c", f"apt-get update && apt-get install -y curl && /app/scripts/import-dataset-{type}.sh"],
            volumes=[existing_volume, configmap_volume],
            volume_mounts=[VolumeMount(name=self.environment.compute_dataset_volume_name(configuration), mount_path="/app/scripts")]

        )