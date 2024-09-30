import uuid

class layout:
    @staticmethod
    def rename_resource(base_name: str) -> str:
        # Transform the base name into a valid k8s resource name
        # keeps only the first part of the name until the first '@' (the sha256 part, if any)
        return base_name.replace(":", "-").replace("/", "-").split("@")[0]

    @staticmethod
    def create_container_name(constant, version, product, step, variability):
        return f'{layout.rename_resource(constant)}-{layout.create_database_identifier(version, product, step, variability)}'

    @staticmethod
    def create_database_identifier(version, product, step, variability):
        return f"{version}-{product}-{step}-{variability}".lower()
    
    @staticmethod
    def create_postgres_container_name(version, product, step, variability):
        return layout.create_container_name('postgres', version, product, step, variability)
    
    @staticmethod
    def create_blazegraph_container_name(version, product, step, variability):
        return layout.create_container_name('vcity-blazegraph', version, product, step, variability)
