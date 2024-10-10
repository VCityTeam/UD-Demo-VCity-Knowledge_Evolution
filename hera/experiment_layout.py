import uuid

class layout:
    @staticmethod
    def rename_resource(base_name: str) -> str:
        # Transform the base name into a valid k8s resource name
        # keeps only the first part of the name until the first '@' (the sha256 part, if any)
        return base_name.replace(":", "-").replace("/", "-").split("@")[0]

    @staticmethod
    def create_name(constant, configuration):
        return f'{layout.rename_resource(constant)}-{layout.create_database_identifier(configuration)}'

    @staticmethod
    def create_database_identifier(configuration):
        return str(configuration).lower()

    @staticmethod
    def create_relational_database_url(configuration):
        host = layout.create_postgres_service_name(configuration)
        return f'jdbc:postgresql://{host}:5432/{layout.create_database_identifier(configuration)}'
    
    @staticmethod
    def create_service_remover_name(configuration):
        return f"{layout.create_name('service-remover', configuration)}"
    
    @staticmethod
    def create_postgres_container_name(configuration):
        return f"{layout.create_name('postgres', configuration)}-container"
    
    @staticmethod
    def create_postgres_service_name(configuration):
        return f"{layout.create_name('postgres', configuration)}-service"
    
    @staticmethod
    def create_quader_container_name(configuration):
        return f"{layout.create_name('quader', configuration)}-container"
    
    @staticmethod
    def create_quader_service_name(configuration):
        return f"{layout.create_name('quader', configuration)}-service"
    
    @staticmethod
    def create_quaque_container_name(configuration):
        return f"{layout.create_name('quaque', configuration)}-container"
    
    @staticmethod
    def create_quaque_service_name(configuration):
        return f"{layout.create_name('quaque', configuration)}-service"
    
    @staticmethod
    def create_blazegraph_container_name(configuration):
        return f"{layout.create_name('vcity-blazegraph', configuration)}-container"
    
    @staticmethod
    def create_blazegraph_service_name(configuration):
        return f"{layout.create_name('vcity-blazegraph', configuration)}-service"
    
    @staticmethod
    def create_bsbm_container_name(configuration):
        return f"{layout.create_name('bsbm', configuration)}-container"
    
    @staticmethod
    def create_querier_container_name(configuration):
        return f"{layout.create_name('querier', configuration)}-container"
    
    @staticmethod
    def create_typed_transformer_container_name(configuration, type):
        return f"{layout.create_name(f'{type}-transformer', configuration)}-container"

    @staticmethod
    def create_typed_importer_container_name(configuration, type):
        return f"{layout.create_name(f'{type}-importer', configuration)}-container"