import uuid

class layout:
    @staticmethod
    def rename_resource(base_name: str) -> str:
        # Transform the base name into a valid k8s resource name
        # keeps only the first part of the name until the first '@' (the sha256 part, if any)
        return base_name.replace(":", "-").replace("/", "-").split("@")[0]

    @staticmethod
    def create_container_name(constant, configuration):
        return f'{layout.rename_resource(constant)}-{layout.create_database_identifier(configuration)}'

    @staticmethod
    def create_database_identifier(configuration):
        return str(configuration).lower()

    @staticmethod
    def create_relational_database_url(configuration):
        host = layout.create_container_name('postgres', configuration)
        return f'jdbc:postgresql://{host}:5432/{layout.create_database_identifier(configuration)}'
    
    @staticmethod
    def create_postgres_container_name(configuration):
        return layout.create_container_name('postgres', configuration)
    
    @staticmethod
    def create_quader_container_name(configuration):
        return layout.create_container_name('quader', configuration)
    
    @staticmethod
    def create_quaque_container_name(configuration):
        return layout.create_container_name('quaque', configuration)
    
    @staticmethod
    def create_blazegraph_container_name(configuration):
        return layout.create_container_name('vcity-blazegraph', configuration)
    
    @staticmethod
    def create_bsbm_container_name(configuration):
        return layout.create_container_name('bsbm', configuration)
