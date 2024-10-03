import types
import os

constants = types.SimpleNamespace(
    postgres = "postgres@sha256:4ec37d2a07a0067f176fdcc9d4bb633a5724d2cc4f892c7a2046d054bb6939e5",
    blazegraph = "vcity/blazegraph-cors@sha256:c6f9556ca53ff01304557e349d2f10b3e121dae7230426f4c64fa42b2cbaf805",
    quader = "vcity/quads-loader@sha256:9ddb6b97427b0a6c973345ef5797e1f0fa5f8b1e456e8ef17ccd712d827896e8",
    quaque = "vcity/quads-query@sha256:c0cbd3be07022fc6eea2bdffd43d3c99e97b9742e2ebec81ed387002bbbc404d",
    bsbm = "vcity/bsbm@sha256:57dbf7fb5437e7e83be36f9c566bdfa55d7dc1b82d03869ca8d491eaffa15e14",
    quads_transformer = "vcity/quads-creator@sha256:cb63460db2c640c0708a95a9db16b9571c9c156603890896dd12341f1ebf9a00", 
    postgres_username = os.environ.get('POSTGRES_USER', "postgres"),
    postgres_password = os.environ.get('POSTGRES_PASSWORD', "password"),
)