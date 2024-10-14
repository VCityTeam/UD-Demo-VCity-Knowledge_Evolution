from hera.workflows import (
    Container,
    models,
    ExistingVolume,
    Resource,
    script,
    Parameter,
    Resources
)
from experiment_utils import create_volume_manifest
from experiment_layout import layout
from environment import environment
from configuration import configuration
from itertools import product


@script(
    image="{{inputs.parameters.python_requests_image}}",
    inputs=[
        Parameter(name="python_requests_image", description="The name of the Python image to use"),
        Parameter(name="existing_volume_name", description="The name of the existing volume containing the data to import"),
        Parameter(name="number_of_versions", description="The number of versions to import"),
        Parameter(name="hostname", description="The hostname of the server to import the data into"),
    ],
    volumes=[
        ExistingVolume(
            name="{{inputs.parameters.existing_volume_name}}",
            claim_name="{{inputs.parameters.existing_volume_name}}",
            mount_path="/app/data",
        )
    ],
    resources=Resources(memory_request="2Gi")
)
def create_relational_dataset_importer(
    number_of_versions: int,
    hostname: str
) -> None:
    from datetime import datetime
    import os
    import time
    import requests
    import sys

    directory = "/app/data/relational"

    try:
        # Get the list of files and directories in the specified directory
        files_and_directories = os.listdir(directory)
        
        # Filter out directories, keeping only files
        files = [f for f in files_and_directories if os.path.isfile(os.path.join(directory, f))]

        # Print the files
        for file in files:
            if file.endswith(".ttl.relational.trig"):
                # Extraire le numéro de version à partir du nom de fichier
                version = int(file.split('-')[-1].split('.ttl')[0])

                # Vérifier si la version est inférieure ou égale au nombre de versions spécifiées
                if version <= number_of_versions:
                    print(f"\n{datetime.now().isoformat()} - [quads-loader] Version {file}")
                    start = int(time.time() * 1000)
                    filepath = os.path.join(directory, file)

                    # Effectuer la requête HTTP pour importer la version
                    try:
                        with open(filepath, 'rb') as f:
                            response = requests.post(
                                f'http://{hostname}:8080/import/version',
                                files=dict(file=f)
                            )
                            response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to import {filepath}: {e}")
                        sys.exit(1)

                    end = int(time.time() * 1000)
                    print(f"\n{datetime.now().isoformat()} - [Measure] (Import STS {file}): {end-start}ms;")
    except Exception as e:
        print(f"An error occurred: {e}")

@script(
    image="{{inputs.parameters.python_requests_image}}",
    inputs=[
        Parameter(name="python_requests_image", description="The name of the Python image to use"),
        Parameter(name="existing_volume_name", description="The name of the existing volume containing the data to import"),
        Parameter(name="number_of_versions", description="The number of versions to import"),
        Parameter(name="hostname", description="The hostname of the server to import the data into"),
    ],
    volumes=[
        ExistingVolume(
            name="{{inputs.parameters.existing_volume_name}}",
            claim_name="{{inputs.parameters.existing_volume_name}}",
            mount_path="/app/data",
        )
    ],
    resources=Resources(memory_request="2Gi")
)
def create_theoretical_dataset_importer(
    number_of_versions: int,
    hostname: str
) -> None:
    from datetime import datetime
    import os
    import time
    import requests
    import sys

    directory = "/app/data/theoretical"

    try:
        # Get the list of files and directories in the specified directory
        files_and_directories = os.listdir(directory)
        
        # Filter out directories, keeping only files
        files = [f for f in files_and_directories if os.path.isfile(os.path.join(directory, f))]

        for file in files:
            if file.endswith(".ttl.theoretical.trig"):
                # Extraire le numéro de version à partir du nom de fichier
                version = int(file.split('-')[-1].split('.ttl')[0])

                # Vérifier si la version est inférieure ou égale au nombre de versions spécifiées
                if version <= number_of_versions:
                    print(f"\n{datetime.now().isoformat()} - [Triple Store] Version {file}")
                    start = int(time.time() * 1000)
                    filepath = os.path.join(directory, file)

                    # Effectuer la requête HTTP pour importer la version
                    try:
                        with open(filepath, 'r') as f:
                            response = requests.post(
                                f'http://{hostname}:9999/blazegraph/sparql',
                                headers={'Content-Type': 'application/x-trig'},
                                data=f.read(),
                            )
                            response.raise_for_status()
                    except requests.exceptions.RequestException as e:
                        print(f"Failed to import {filepath}: {e}")
                        sys.exit(1)

                    end = int(time.time() * 1000)
                    print(f"\n{datetime.now().isoformat()} - [Measure] (Import BG {file}): {end-start}ms;")
    except Exception as e:
        print(f"An error occurred: {e}")

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
            manifest = create_volume_manifest(
                self.environment.compute_dataset_volume_name(configuration),
                "ReadWriteOnce",
                self.environment.compute_dataset_volume_size(configuration)
            )

            Resource(
                name=self.environment.compute_dataset_volume_name(configuration),
                action="create",
                set_owner_reference=True,
                manifest=manifest
            )

    def create_logging_volumes(self, configurations: list[configuration]) -> None:
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
            manifest = create_volume_manifest(
                self.environment.compute_logging_volume_name(configuration),
                "ReadWriteOnce",
                self.environment.compute_dataset_volume_size(configuration)
            )

            Resource(
                name=self.environment.compute_logging_volume_name(configuration),
                action="create",
                set_owner_reference=True,
                manifest=manifest
            )

    def create_datasets_generator_containers(self, configurations: list[configuration], constants) -> None:        
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
                volumes=[volume_mount],
                resources=Resources(memory_request="4Gi", cpu_request="2")
            )

    def generate_datasets_configurations(self, arguments: object) -> list[configuration]:
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
    
    def create_datasets_transformers_containers(self, configurations: list[configuration], constants) -> None:        
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
            self.create_typed_dataset_transformer_container(configuration, constants, 'relational')
            self.create_typed_dataset_transformer_container(configuration, constants, 'theoretical')
    
    def create_typed_dataset_transformer_container(self, configuration: configuration, constants, type: str) -> None:
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
            volumes=[volume_mount],
            resources=Resources(memory_request="4Gi", cpu_request="2")
        )

