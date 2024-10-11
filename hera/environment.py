from hera_utils import k8s_cluster
from hera_utils import num_exp_environment, Struct
from configuration import configuration

class environment(num_exp_environment):

    def __init__(self, args, verbose=False):

        num_exp_environment.__init__(self, args, verbose)

        k8s = k8s_cluster(args)
        k8s.assert_cluster()

        ### A persistent volume (defined at the k8s level) can be used by
        # tasks of a workflow in order to flow output results from an upstream
        # task to a downstream one, and persist once the workflow is finished
        self.persisted_volume = Struct()
        k8s.assert_volume_claim(args.k8s_dataset_volume_claim_name)
        self.persisted_volume.claim_name = args.k8s_dataset_volume_claim_name

        # The mount path is technicality standing in between Environment and
        # Experiment related notions: more precisely it is a technicality that
        # should be dealt by the (Experiment) Conductor (refer to
        # https://gitlab.liris.cnrs.fr/expedata/expe-data-project/-/blob/master/lexicon.md#conductor )
        self.persisted_volume.mount_path = "/data"

    def compute_dataset_volume_name(self, configuration: configuration):
        return f"volume-{configuration.product}-{configuration.version}-{configuration.step}-{configuration.variability}"

    def compute_logging_volume_name(self, configuration: configuration):
        return f"logging-{configuration.product}-{configuration.version}-{configuration.step}-{configuration.variability}"

    def compute_configmap_volume_name(self, configuration: configuration, type: str):
        return f"configmap-{type}-{configuration.product}-{configuration.version}-{configuration.step}-{configuration.variability}"

    def compute_dataset_volume_size(self, configuration: configuration):
        number_of_datasets = 3 # (triples + quads(relational) + quads(graph))
        number_of_triples_one_version = configuration.product + configuration.step * configuration.version
        size_one_triple = 0.05 # Mi
        total = (number_of_triples_one_version * size_one_triple) * (configuration.version * number_of_datasets)
        return f'{total}Mi'

    def compute_logging_volume_size(self, configuration: configuration):
        number_of_iterations = 2 # (import + queries)
        number_of_quads_one_version = configuration.product + configuration.step * configuration.version
        size_one_quad_log = 0.075 # Mi
        total = (number_of_quads_one_version * size_one_quad_log) * (configuration.version * number_of_iterations)
        return f'{total}Mi'

    def database_data(self, configuration):
        return f"{self.persisted_volume.mount_path}/{str(configuration)}"