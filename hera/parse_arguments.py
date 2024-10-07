import os
import sys
import logging
import hera_utils


def parse_arguments(logger=logging.getLogger(__name__)):
    """Extend the default parser with the local needs"""
    parser = hera_utils.define_parser(logger)

    # Add the locally defined parser extensions
    parser.add(
        "--k8s_dataset_volume_claim_name",
        help="Name of the k8s volume claim to be used by numerical experiment to store the dataset.",
        type=str,
    )

    parser.add(
        "--versions",
        help="List of versions to be used in the numerical experiment",
        type=int,
        nargs="+",
    )

    parser.add(
        "--products",
        help="List of BSBM products to be used in the numerical experiment",
        type=int,
        nargs="+",
    )

    parser.add(
        "--steps",
        help="List of BSBM products steps to be used in the numerical experiment",
        type=int,
        nargs="+",
    )

    parser.add(
        "--variabilities",
        help="List of BSBM products variability to be used in the numerical experiment",
        type=int,
        nargs="+",
    )

    # Parse and assert that the default parser is satisfied
    args = parser.parse_args()
    args_are_correct = hera_utils.verify_args(args)
    if not args_are_correct:
        parser.print_help()
        sys.exit()

    return args
