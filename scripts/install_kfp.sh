#!/usr/bin/env bash
set -euo pipefail

KFP_VERSION="2.3.0"
NAMESPACE="kubeflow"

kubectl create namespace "${NAMESPACE}" || true

# Cluster-scoped resources
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=${KFP_VERSION}"

# Dev env (single-cluster)
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/dev?ref=${KFP_VERSION}"

# Wait for UI (optional)
kubectl -n "${NAMESPACE}" rollout status deploy/ml-pipeline-ui --timeout=5m

echo "Port forward UI:"
echo "kubectl -n ${NAMESPACE} port-forward svc/ml-pipeline-ui 8080:80"
echo "Open: http://localhost:8080"
