from hera.workflows import (
    ConfigMapEnvFrom,
    ExistingVolume,
    Parameter,
    script,
)

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
