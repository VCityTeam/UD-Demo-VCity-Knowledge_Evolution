import types
import os

constants = types.SimpleNamespace(
    postgres = "postgres@sha256:4ec37d2a07a0067f176fdcc9d4bb633a5724d2cc4f892c7a2046d054bb6939e5",
    blazegraph = "vcity/blazegraph-cors@sha256:c6f9556ca53ff01304557e349d2f10b3e121dae7230426f4c64fa42b2cbaf805",
    quader = "vcity/quads-loader@sha256:306a33f8853bc8249c4f607e68f8239569af9afa80eb93940b18abb24ae1a37e",
    quaque = "vcity/quads-query@sha256:c0cbd3be07022fc6eea2bdffd43d3c99e97b9742e2ebec81ed387002bbbc404d",
    bsbm = "vcity/bsbm@sha256:34665c65bbb2bfbf4348e19a23de9c51a0eb8fafc6d90802c2eda3522f9c420c",
    quads_transformer = "vcity/quads-creator@sha256:ddfa89f708bb311f07abbf587bc65542469b45828399c9e3cf0d9544c52e1167", 
    postgres_username = os.environ.get('POSTGRES_USER', "postgres"),
    postgres_password = os.environ.get('POSTGRES_PASSWORD', "password"),
    ubuntu = "ubuntu@sha256:c62f1babc85f8756f395e6aabda682acd7c58a1b0c3bea250713cd0184a93efa",
    python_requests = "xr09/python-requests@sha256:61a5289993bbbfbe4ab3299428855b83c490aeb277895c2bb6f16ab5f0f74abd",
    quads_querier = "harbor.pagoda.os.univ-lyon1.fr/ud-evolution/quads-querier:v1.1.0"
)