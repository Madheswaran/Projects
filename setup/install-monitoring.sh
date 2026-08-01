#!/bin/bash

set -e

PROM_VERSION="88.0.1"

echo "========================================="
echo "Installing Kubernetes Monitoring Stack"
echo "========================================="

####################################################
# Check prerequisites
####################################################

if ! command -v kubectl &> /dev/null
then
    echo "ERROR: kubectl is not installed."
    exit 1
fi

if ! command -v helm &> /dev/null
then
    echo "ERROR: Helm is not installed."
    exit 1
fi

####################################################
# Create Monitoring Namespace
####################################################

echo ""
echo "Creating monitoring namespace..."

kubectl create namespace monitoring \
    --dry-run=client \
    -o yaml | kubectl apply --validate=false -f -

####################################################
# Add Helm Repository
####################################################

echo ""
echo "Adding Prometheus Helm repository..."

helm repo add prometheus-community \
https://prometheus-community.github.io/helm-charts \
2>/dev/null || true

####################################################
# Install Prometheus CRDs
####################################################

echo ""
echo "Installing Prometheus CRDs..."

helm show crds \
./setup/charts/kube-prometheus-stack-88.0.1.tgz \
| kubectl apply --server-side -f -

echo ""

sleep 15

echo "Installed CRDs"

kubectl get crd | grep monitoring.coreos

####################################################
# Install kube-prometheus-stack
####################################################

echo ""
echo "Installing Prometheus Stack..."

helm upgrade --install monitoring \
./setup/charts/kube-prometheus-stack-88.0.1.tgz \
--namespace monitoring \
--create-namespace \
--wait \
--timeout 20m

echo ""

kubectl wait \
--namespace monitoring \
--for=condition=Ready \
pod \
--all \
--timeout=1200s

echo ""

kubectl get pods -n monitoring

####################################################
# Install Prometheus CRDs
####################################################

# echo ""
# echo "Installing Prometheus Operator CRDs..."

# helm show crds \
# prometheus-community/kube-prometheus-stack \
# --version ${PROM_VERSION} \
# | kubectl apply \
# --server-side \
# --validate=false \
# -f -

# echo ""
# echo "Waiting for CRDs to register..."

# sleep 20

# ####################################################
# # Verify CRDs
# ####################################################

# echo ""
# echo "Installed Prometheus CRDs"

# kubectl get crd | grep monitoring.coreos

# ####################################################
# # Install kube-prometheus-stack
# ####################################################

# echo ""
# echo "Installing Prometheus Stack..."

# helm upgrade --install monitoring \
# prometheus-community/kube-prometheus-stack \
# --version ${PROM_VERSION} \
# --namespace monitoring \
# --create-namespace \
# --disable-openapi-validation \
# --wait \
# --timeout 20m \
# --debug

####################################################
# Wait for Pods
####################################################

echo ""
echo "Waiting for Monitoring Pods..."

kubectl wait \
--namespace monitoring \
--for=condition=Ready \
pod \
--all \
--timeout=1200s

####################################################
# Display Pods
####################################################

echo ""
echo "Monitoring Pods"

kubectl get pods -n monitoring

####################################################
# Display Services
####################################################

echo ""
echo "Monitoring Services"

kubectl get svc -n monitoring

####################################################
# Grafana Credentials
####################################################

echo ""
echo "Grafana Credentials"

echo "Username : admin"

echo -n "Password : "

kubectl get secret monitoring-grafana \
-n monitoring \
-o jsonpath="{.data.admin-password}" | base64 -d

echo ""

####################################################
# Access URLs
####################################################

echo ""
echo "========================================="
echo "Installation Complete"
echo "========================================="

echo ""
echo "Grafana Port Forward"
echo "kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring"

echo ""
echo "Prometheus Port Forward"
echo "kubectl port-forward svc/monitoring-kube-prometheus-prometheus 9090:9090 -n monitoring"

echo ""
echo "Grafana   : http://localhost:3000"
echo "Prometheus: http://localhost:9090"