from hera.workflows import (
    script,
)

@script()
def print_environment(parameters: object):
    import json

    print("Printing workflow parameters:")
    print("parameters: ", json.dumps(parameters, sort_keys=True))

@script()
def print_instance_args(arguments: object):
    import json

    print("Printing instance arguments:")
    print("arguments: ", json.dumps(arguments, sort_keys=True))