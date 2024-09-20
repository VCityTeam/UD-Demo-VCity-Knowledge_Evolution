import uuid

class layout:
    @staticmethod
    def database_name(version, product, step, variability):
        return f"{version}-{product}-{step}-{variability}".lower()

    @staticmethod
    def create_database_identifier(version, product, step, variability):
        return f"{version}-{product}-{step}-{variability}-{uuid.uuid4().hex[:8]}".lower()
