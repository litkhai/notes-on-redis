#!/usr/bin/env bash
# Remove everything: the kind cluster holds the operator, the databases, RDI and Postgres.
kind delete cluster --name nor-rec
