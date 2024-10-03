from hera.workflows import (
    Container,
    models,
    ExistingVolume
)
from experiment_layout import layout
from environment import environment
from configuration import configuration

class datasets:
    def __init__(self, layout: layout, environment: environment):
        self.layout = layout
        self.environment = environment

    def create_datasets_containers(self, configurations: list[configuration], constants) -> None:        
        for configuration in configurations:
            bsbm_container_name = self.layout.create_bsbm_container_name(configuration)

            volume_mount = ExistingVolume(
                name=self.environment.persisted_volume.claim_name,
                claim_name=self.environment.persisted_volume.claim_name,
                mount_path=f"/app/data/{self.layout.create_bsbm_container_name(configuration)}"
            )

            Container(
                name=bsbm_container_name,
                image=constants.bsbm,
                image_pull_policy=models.ImagePullPolicy.always,
                args=["generate-n", configuration.version, configuration.product, configuration.step, configuration.variability],
                volumes=[volume_mount]
            )

    def generate_datasets_configurations(self, arguments: object) -> list:
        from itertools import product

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
        for configuration in configurations:
            self.create_typed_dataset_transformer(configuration, constants, 'relational')
            self.create_typed_dataset_transformer(configuration, constants, 'theoretical')
    
    def create_typed_dataset_transformer(self, configuration: configuration, constants, type: str) -> None:
        if (type != "relational" and type != "theoretical"):
            raise Exception(f"Unknown dataset type: {type}")

        typed_transformer_container_name = self.layout.create_typed_transformer_container_name(configuration, type)

        volume_mount = ExistingVolume(
            name=self.environment.persisted_volume.claim_name,
            claim_name=self.environment.persisted_volume.claim_name,
            mount_path=f"/app/data/{self.layout.create_bsbm_container_name(configuration)}"
        )

        Container(
            name=typed_transformer_container_name,
            image=constants.quads_transformer,
            image_pull_policy=models.ImagePullPolicy.always,
            args=[
                f"/app/data/{self.layout.create_bsbm_container_name(configuration)}/{type}",
                f"/app/data/{self.layout.create_bsbm_container_name(configuration)}",
                "*",
                type,
                "BSBM"
            ],
            volumes=[volume_mount]
        )
