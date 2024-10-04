import sys
import experiment_layout
from parse_arguments import parse_arguments
from environment import environment
from experiment_constants import constants
from experiment_utils import print_environment, print_instance_args
from databases import databases
from servers import servers
from datasets import datasets
from hera.workflows import (
    Task,
    DAG,
    Workflow,
)

if __name__ == "__main__":
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

    experiment_dbs = databases(layout, environment)
    experiment_servers = servers(layout, environment)
    experiment_datasets = datasets(layout, environment)

    dbs_configurations = experiment_dbs.generate_databases_configurations(parameters)
    datasets_configurations = experiment_datasets.generate_datasets_configurations(parameters)

    with Workflow(generate_name="converg-experiment-", entrypoint="converg-step") as w:
        # function building all the database containers/services
        experiment_dbs.create_dbs_containers_services(dbs_configurations, constants)
        # function building all the server containers/services
        experiment_servers.create_servers_containers_services(dbs_configurations, constants)
        # function building all the dataset volumes
        experiment_datasets.create_datasets_volumes(datasets_configurations)
        # function building all the dataset containers
        experiment_datasets.create_datasets_containers(datasets_configurations, constants)
        # function building all the dataset transformers
        experiment_datasets.create_datasets_transformers(datasets_configurations, constants)

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
                
                # init all the datasets volumes
                volume_mount = environment.compute_dataset_volume_name(ds_configuration)
                # init all the datasets (bsbm)
                bsbm_container_name = layout.create_bsbm_container_name(ds_configuration)
                # transform the datasets
                relational_transformer_container_name = layout.create_typed_transformer_container_name(ds_configuration, 'relational')
                theoretical_transformer_container_name = layout.create_typed_transformer_container_name(ds_configuration, 'theoretical')

                task_volume = Task(name=f'{volume_mount}-volume-task', template=volume_mount)
                task_bsbm = Task(name=f'{bsbm_container_name}-task', template=bsbm_container_name)
                task_relational_transformer = Task(name=f'{relational_transformer_container_name}-task', template=relational_transformer_container_name)
                task_theoretical_transformer = Task(name=f'{theoretical_transformer_container_name}-task', template=theoretical_transformer_container_name)

                print_env >> print_inst >> task_volume >> task_bsbm >> task_relational_transformer >> task_theoretical_transformer
            
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

                blazegraph_container_name = layout.create_blazegraph_container_name(db_configuration)

                # init all the servers (quader and quaque)
                quader_container_name = layout.create_quader_container_name(db_configuration)
                quaque_container_name = layout.create_quaque_container_name(db_configuration)

                # create the tasks for the databases and their services
                task_pg_c = Task(name=f'{postgres_container_name}-container-task', template=postgres_container_name)
                task_pg_s = Task(name=f'{postgres_container_name}-service-task', template=postgres_container_name)
                task_bg_c = Task(name=f'{blazegraph_container_name}-container-task', template=blazegraph_container_name)
                task_bg_s = Task(name=f'{blazegraph_container_name}-service-task', template=blazegraph_container_name)

                # create the tasks for the servers and their services
                task_quader_c = Task(name=f'{quader_container_name}-container-task', template=quader_container_name)
                task_quader_s = Task(name=f'{quader_container_name}-service-task', template=quader_container_name)
                task_quaque_c = Task(name=f'{quaque_container_name}-container-task', template=quaque_container_name)
                task_quaque_s = Task(name=f'{quaque_container_name}-service-task', template=quaque_container_name)

                flow_relational = task_pg_s >> task_pg_c >> task_quader_s >> task_quader_c >> task_quaque_s >> task_quaque_c
                flow_triple = task_bg_s >> task_bg_c

                print_env >> print_inst >> [flow_relational, flow_triple]
        
        w.create()
