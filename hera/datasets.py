from hera.workflows import (
    Container,
    models
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

            Container(
                name=bsbm_container_name,
                image=constants.bsbm,
                image_pull_policy=models.ImagePullPolicy.always,
                args=["generate-n", configuration.version, configuration.product, configuration.step, configuration.variability]
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