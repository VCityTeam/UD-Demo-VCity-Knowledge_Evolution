from hera.workflows import (
    ConfigMapEnvFrom,
    ExistingVolume,
    Parameter,
    script,
)
from configuration import configuration

@script(
    env_from=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ],
)
def assert_configmap_environment(
    # Config_map_name argument is only used by the @script decorator and is
    # present here only because Hera seems to require it
    config_map_name,
):
    import os
    import sys
    import json

    environment_variables = dict(os.environ)
    if "HTTPS_PROXY" in environment_variables:
        print("HTTPS_PROXY environment variable found and (probably) defined")
        print("in the ", config_map_name, " ConfigMap.")
        print("HTTPS_PROXY value: ", environment_variables["HTTPS_PROXY"])
    else:
        print("HTTPS_PROXY environment variable NOT found.")
        print(
            "Something went wrong when defining of accessing the ",
            config_map_name,
            " ConfigMap.",
        )
        print("List of retrieved environment variables: ")
        print(json.dumps(dict(os.environ), indent=4))
        sys.exit(1)
    print("Exiting (from print_environment script).")


@script(
    inputs=[
        Parameter(name="claim_name"),
        Parameter(name="mount_path"),
    ],
    env_from=[
        # Assumes the corresponding config map is defined at k8s level
        ConfigMapEnvFrom(
            name="{{inputs.parameters.config_map_name}}",
            optional=False,
        )
    ],
    volumes=[
        ExistingVolume(
            name="dummy",
            claim_name="{{inputs.parameters.claim_name}}",
            mount_path="{{inputs.parameters.mount_path}}",
        )
    ],
)
def does_the_mounted_appear_in_list(
    # claim_name argument is only used by the @script decorator and is present
    # here only because Hera seems to require it
    config_map_name,
    claim_name,
    mount_path,
):
    import subprocess
    import sys
    import os

    # Installing a package with pip requires an http access to PyPi (by default)
    # which can be blocked by the cluster networking configuration and might
    # thus require the configuration of an http proxy server.
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    print("Psutil python package successfully installed.")
    import psutil

    volume_present = set(
        filter(
            lambda x: str(x.mountpoint) == mount_path,
            psutil.disk_partitions(),
        )
    )
    if len(volume_present) == 1:
        print(f"The persisted volume directory {mount_path} was duly mounted")
        sys.exit(0)

    # The persisted volume directory does NOT seem to be properly mounted
    # but this could be due to a failure of usage of
    # psutil.disk_partitions(). Let use assume this is the case and still
    # try to assert that the directory exists and is accessible:
    if not os.path.isdir(mount_path):
        print(f"Persisted volume directory {mount_path} not found.")
        print("Exiting")
        sys.exit(1)

    # Just to give some debug feedback by listing the files
    # Refer to
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
    # for the one liner on listing files (e.g. `os.listdir(mount_path)`).
    filenames = next(os.walk(mount_path), (None, None, []))[2]
    print(f"Persisted volume directory file access check: {filenames}")
    print(f"The persisted volume directory {mount_path} was properly mounted.")

def create_postgres_container_service(configuration: configuration, constants) -> None:
    postgres_container_name = layout.create_postgres_container_name(configuration)
    postgres_service_name = layout.create_postgres_service_name(configuration)
    Container(
        name=postgres_container_name,
        image=constants.postgres,
        image_pull_policy=models.ImagePullPolicy.always,
        daemon=True,
        env=[
            Env(
                name="POSTGRES_DB",
                value=layout.create_database_identifier(configuration),
            ),
            Env(name="POSTGRES_PASSWORD", value="password"), # FIXME: Use a secret
            Env(name="POSTGRES_USER", value="user"), # FIXME: Use a secret
            Env(name="PGDATA", value=environment.database_data(configuration)),
        ],
        env_from=[
            # Assumes the corresponding config map is defined at k8s level
            ConfigMapEnvFrom(
                name=environment.cluster.proxy_configmap,
                optional=False,
            )
        ],
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

def create_blazegraph_container_service(configuration: configuration, constants) -> None:
    blazegraph_container_name = layout.create_blazegraph_container_name(configuration)
    blazegraph_service_name = layout.create_blazegraph_service_name(configuration)

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

def create_dbs_containers_services(configurations: list, constants) -> None:
    for configuration in configurations:
        create_postgres_container_service(configuration, constants)
        create_blazegraph_container_service(configuration, constants)

def create_servers_containers(configurations: list, constants) -> None:
    for configuration in configurations:
        quader_container_name = layout.create_quader_container_name(configuration)
        quaque_container_name = layout.create_quaque_container_name(configuration)

        Container(
            name=quader_container_name,
            image=constants.quader,
            image_pull_policy=models.ImagePullPolicy.always,
            daemon=True,
            env=[
                Env(
                    name="SPRING_DATASOURCE_URL",
                    value=layout.create_relational_database_url(configuration),
                ),
                Env(name="SPRING_DATASOURCE_PASSWORD", value="password"), # FIXME: Use a secret
                Env(name="SPRING_DATASOURCE_USERNAME", value="user"), # FIXME: Use a secret
            ],
            env_from=[
                # Assumes the corresponding config map is defined at k8s level
                ConfigMapEnvFrom(
                    name=environment.cluster.proxy_configmap,
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

def create_datasets_containers(configurations: list, constants) -> None:
    for configuration in configurations:
        bsbm_container_name = layout.create_bsbm_container_name(configuration)

        Container(
            name=bsbm_container_name,
            image=constants.bsbm,
            image_pull_policy=models.ImagePullPolicy.always,
            args=["generate-n", configuration.version, configuration.product, configuration.step, configuration.variability]
        )

@script()
def print_environment(parameters: object):
    import json

    print("Printing workflow parameters:")
    print("parameters: ", json.dumps(parameters, indent=4))

@script()
def print_instance_args(arguments: object):
    import json

    print("Printing instance arguments:")
    print("arguments: ", json.dumps(arguments, indent=4))

def generate_databases_configurations(parameters: object) -> list:
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

def generate_datasets_configurations(arguments: object) -> list:
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


@script()
def consume(version: int, product: int, step: int, variability: int, postgres: str, blazegraph: str):
    print("Received version={version}, product={product}, step={step}, variability={variability}"
          .format(version=version, product=product, step=step, variability=variability)
    )

if __name__ == "__main__":
    # A workflow that tests whether the defined environment is correct as
    # seen and used from within the Argo server engine (at Workflow runtime)
    import sys
    import experiment_layout
    from parse_arguments import parse_arguments
    from environment import environment
    from experiment_constants import constants
    from hera.workflows import (
        Task,
        DAG,
        Container,
        Resource,
        ConfigMapEnvFrom,
        Workflow,
        Env,
        models
    )

    args = parse_arguments()

    environment = environment(args)
    layout = experiment_layout.layout()

    # # Map the arguments to the parameters that shall be used in the workflow
    parameters = {
        "versions": args.versions,
        "products": args.products,
        "steps": args.steps,
        "variabilities": args.variabilities
    }

    dbs_configurations = generate_databases_configurations(parameters)
    datasets_configurations = generate_datasets_configurations(parameters)

    with Workflow(generate_name="converg-experiment-", entrypoint="converg-step") as w:
        # function building all the database containers/services
        create_dbs_containers_services(dbs_configurations, constants)
        # function building all the server containers/services
        create_servers_containers(dbs_configurations, constants)
        # function building all the dataset containers
        create_datasets_containers(datasets_configurations, constants)

        with DAG(name="converg-step"):
            print_env = print_environment(name="print-environment", arguments={"parameters": parameters})

            for ds_configuration in datasets_configurations:
                instance_args = {
                    "version": ds_configuration.version,
                    "product": ds_configuration.product,
                    "step": ds_configuration.step,
                    "variability": ds_configuration.variability
                }
                print_inst = print_instance_args(name=f'print-ds-instance-args-{str(ds_configuration)}', arguments={"arguments": instance_args})

                # init all the datasets (bsbm)
                bsbm_container_name = layout.create_bsbm_container_name(ds_configuration)

                task_bsbm = Task(name=f'{bsbm_container_name}-task', template=bsbm_container_name)

                print_env >> print_inst >> task_bsbm
            
            for db_configuration in dbs_configurations:
                instance_args = {
                    "version": db_configuration.version,
                    "product": db_configuration.product,
                    "step": db_configuration.step,
                    "variability": db_configuration.variability,
                    "postgres": constants.postgres,
                    "blazegraph": constants.blazegraph,
                    "quaque": constants.quaque,
                    "quader": constants.quader,
                }
                print_inst = print_instance_args(name=f'print-db-instance-args-{str(db_configuration)}', arguments={"arguments": instance_args})
                
                # init all the databases and services (postgresql and blazegraph)
                postgres_container_name = layout.create_postgres_container_name(db_configuration)
                postgres_service_name = layout.create_postgres_service_name(db_configuration)

                blazegraph_container_name = layout.create_blazegraph_container_name(db_configuration)
                blazegraph_service_name = layout.create_blazegraph_service_name(db_configuration)

                # init all the servers (quader and quaque)
                quader_container_name = layout.create_quader_container_name(db_configuration)
                quaque_container_name = layout.create_quaque_container_name(db_configuration)

                # create the tasks for the databases/services
                task_pg_c = Task(name=f'{postgres_container_name}-task', template=postgres_container_name)
                task_pg_s = Task(name=f'{postgres_service_name}-task', template=postgres_service_name)
                task_bg_c = Task(name=f'{blazegraph_container_name}-task', template=blazegraph_container_name)
                task_bg_s = Task(name=f'{blazegraph_service_name}-task', template=blazegraph_service_name)

                # create the tasks for the servers
                # task_quader = Task(name=f'{quader_container_name}-task', template=quader_container_name)
                # task_quaque = Task(name=f'{quaque_container_name}-task', template=quaque_container_name)

                print_env >> print_inst >> [task_pg_s >> task_pg_c, task_bg_s >> task_bg_c]
        
        w.create()
