#!/bin/bash

set -euo pipefail

INGRESS_VERSION="4.13.2"
ARGOCD_VERSION="8.3.0"

echo "==============================================="
echo " PayPal Checkout Platform Bootstrap"
echo "==============================================="

ACR_NAME="acrpaypal$(date +%s)"
AKS_NAME="aks-paypal-dev"
SECRET_NAME="acr-secret"

echo
echo "========== Azure Login =========="

az login

echo ""
echo "Available Resource Groups"
echo "--------------------------------"

az group list -o table

RG=$(az group list --query "[0].name" -o tsv)

echo ""
echo "Using Resource Group : $RG"

############################################################
# Create ACR
############################################################

echo ""
echo "========== Creating ACR =========="

if ! az acr show \
--resource-group "$RG" \
--name "$ACR_NAME" >/dev/null 2>&1
then

    az acr create \
    --resource-group "$RG" \
    --name "$ACR_NAME" \
    --sku Basic

    echo ""
    echo "ACR Created"

else

    echo ""
    echo "ACR already exists."

fi

az acr list -o table

############################################################
# Create AKS
############################################################

echo ""
echo "========== Creating AKS =========="

if ! az aks show \
--resource-group "$RG" \
--name "$AKS_NAME" >/dev/null 2>&1
then

    az aks create \
    --resource-group "$RG" \
    --name "$AKS_NAME" \
    --node-count 1 \
    --node-vm-size Standard_D2s_v3 \
    --generate-ssh-keys

    echo ""
    echo "AKS Cluster Created"

else

    echo ""
    echo "AKS already exists."

fi

############################################################
# Get AKS Credentials
############################################################

echo ""
echo "========== Getting AKS Credentials =========="

az aks get-credentials \
--resource-group "$RG" \
--name "$AKS_NAME" \
--overwrite-existing

echo ""
echo "====================================="
echo "POST AKS SETUP STARTED"
echo "====================================="

############################################################
# Dynamic Values
############################################################

ACR_LOGIN_SERVER=$(az acr show \
--name "$ACR_NAME" \
--query loginServer \
-o tsv)

echo ""
echo "Resource Group : $RG"
echo "AKS            : $AKS_NAME"
echo "ACR            : $ACR_NAME"
echo "ACR Login      : $ACR_LOGIN_SERVER"

############################################################
# Enable ACR Admin
############################################################

echo ""
echo "========== Enabling ACR Admin =========="

az acr update \
--name "$ACR_NAME" \
--admin-enabled true

ACR_USERNAME=$(az acr credential show \
--name "$ACR_NAME" \
--query username \
-o tsv)

ACR_PASSWORD=$(az acr credential show \
--name "$ACR_NAME" \
--query passwords[0].value \
-o tsv)

############################################################
# Create Docker Registry Secret
############################################################

echo ""
echo "========== Creating Docker Secret =========="

kubectl delete secret "$SECRET_NAME" \
--ignore-not-found

kubectl create secret docker-registry "$SECRET_NAME" \
--docker-server="$ACR_LOGIN_SERVER" \
--docker-username="$ACR_USERNAME" \
--docker-password="$ACR_PASSWORD"

echo ""
echo "Docker Registry Secret Created"

############################################################
# Install NGINX Ingress (Offline)
############################################################

echo ""
echo "========== Installing Ingress =========="

echo ""
echo "Installing NGINX Ingress..."

helm upgrade --install ingress-nginx \
./setup/charts/ingress-nginx-4.13.2.tgz \
--namespace ingress-nginx \
--create-namespace \
--wait \
--timeout 10m

echo ""
echo "Waiting for Ingress Controller..."

kubectl wait \
--namespace ingress-nginx \
--for=condition=Ready pod \
--selector=app.kubernetes.io/component=controller \
--timeout=300s

kubectl get all -n ingress-nginx

############################################################
# Install ArgoCD (Offline)
############################################################

echo ""
echo "========== Installing ArgoCD =========="

kubectl create namespace argocd \
--dry-run=client \
-o yaml | kubectl apply -f -

echo ""
echo "Checking existing ArgoCD release..."

STATUS=$(helm status argocd \
-n argocd \
2>/dev/null | awk '/^STATUS:/ {print $2}' || true)

if [[ "$STATUS" == "pending-install" || \
      "$STATUS" == "pending-upgrade" || \
      "$STATUS" == "pending-rollback" ]]
then

echo ""
echo "Helm release is stuck in:"
echo "$STATUS"
echo ""
echo "Rollback before continuing."

exit 1

fi

echo ""
echo "Installing ArgoCD..."

helm upgrade --install argocd \
./setup/charts/argo-cd-8.3.0.tgz \
--namespace argocd \
--set server.service.type=LoadBalancer \
--wait \
--timeout 10m

echo ""
echo "Waiting for ArgoCD..."

kubectl wait \
--for=condition=Available deployment/argocd-server \
-n argocd \
--timeout=300s

kubectl wait \
--for=condition=Available deployment/argocd-repo-server \
-n argocd \
--timeout=300s

kubectl wait \
--for=condition=Available deployment/argocd-applicationset-controller \
-n argocd \
--timeout=300s

kubectl get all -n argocd

# ############################################################
# # Install NGINX Ingress
# ############################################################

# echo ""
# echo "========== Installing Ingress =========="

# helm repo add ingress-nginx \
# https://kubernetes.github.io/ingress-nginx \
# 2>/dev/null || true

# echo ""
# echo "Installing NGINX Ingress..."

# helm upgrade --install ingress-nginx \
# ingress-nginx/ingress-nginx \
# --version 4.13.2 \
# --namespace ingress-nginx \
# --create-namespace \
# --disable-openapi-validation \
# --wait \
# --timeout 15m

# echo ""
# echo "Waiting for Ingress Controller..."

# kubectl wait \
# --namespace ingress-nginx \
# --for=condition=Ready pod \
# --selector=app.kubernetes.io/component=controller \
# --timeout=600s

# kubectl get all -n ingress-nginx


# ############################################################
# # Install ArgoCD
# ############################################################

# echo ""
# echo "========== Installing ArgoCD =========="

# helm repo add argo \
# https://argoproj.github.io/argo-helm \
# 2>/dev/null || true

# kubectl create namespace argocd \
# --dry-run=client \
# -o yaml | kubectl apply --validate=false -f -

############################################################
# Check Existing Helm Release
############################################################

# echo ""
# echo "Checking existing ArgoCD release..."

# STATUS=$(helm status argocd \
# -n argocd \
# 2>/dev/null | awk '/^STATUS:/ {print $2}' || true)

# if [[ "$STATUS" == "pending-install" || \
#       "$STATUS" == "pending-upgrade" || \
#       "$STATUS" == "pending-rollback" ]]
# then

#     echo ""
#     echo "======================================================"
#     echo "ERROR"
#     echo ""
#     echo "ArgoCD release is currently:"
#     echo ""
#     echo "    $STATUS"
#     echo ""
#     echo "Rollback first:"
#     echo ""
#     echo "helm history argocd -n argocd"
#     echo "helm rollback argocd <revision> -n argocd"
#     echo ""
#     echo "======================================================"

#     exit 1

# fi

# ############################################################
# # Install / Upgrade ArgoCD
# ############################################################

# echo ""
# echo "Installing ArgoCD..."

# helm upgrade --install argocd \
# argo/argo-cd \
# --version 8.3.0 \
# --namespace argocd \
# --set server.service.type=LoadBalancer \
# --disable-openapi-validation \
# --wait \
# --timeout 15m

# ############################################################
# # Wait for ArgoCD
# ############################################################

# echo ""
# echo "Waiting for ArgoCD..."

# kubectl wait \
# --for=condition=Available \
# deployment/argocd-server \
# -n argocd \
# --timeout=600s

# kubectl wait \
# --for=condition=Available \
# deployment/argocd-repo-server \
# -n argocd \
# --timeout=600s

# kubectl wait \
# --for=condition=Available \
# deployment/argocd-applicationset-controller \
# -n argocd \
# --timeout=600s

# kubectl get all -n argocd

############################################################
# Wait for ArgoCD LoadBalancer IP
############################################################

echo ""
echo "========== Waiting for ArgoCD LoadBalancer =========="

ARGO_IP=""

while true
do

    ARGO_IP=$(kubectl get svc argocd-server \
    -n argocd \
    -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null)

    if [[ -n "$ARGO_IP" ]]
    then
        break
    fi

    echo "Waiting for External IP..."
    sleep 10

done

echo ""
echo "ArgoCD External IP : $ARGO_IP"

############################################################
# Get Initial Admin Password
############################################################

echo ""
echo "========== Getting ArgoCD Admin Password =========="

until kubectl get secret \
argocd-initial-admin-secret \
-n argocd >/dev/null 2>&1
do
    echo "Waiting for Initial Admin Secret..."
    sleep 5
done

ARGO_PASSWORD=$(kubectl get secret \
argocd-initial-admin-secret \
-n argocd \
-o jsonpath="{.data.password}" | base64 -d)

echo ""
echo "====================================="
echo "ARGO USERNAME : admin"
echo "ARGO PASSWORD : $ARGO_PASSWORD"
echo "====================================="

############################################################
# Install ArgoCD CLI
############################################################

echo ""
echo "========== Checking ArgoCD CLI =========="

if ! command -v argocd >/dev/null 2>&1
then

    echo "Installing ArgoCD CLI..."

    curl -sSL \
    -o argocd \
    https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64

    chmod +x argocd

    sudo mv argocd /usr/local/bin/

else

    echo "ArgoCD CLI already installed."

fi

############################################################
# Wait for ArgoCD API
############################################################

echo ""
echo "========== Waiting for ArgoCD API =========="

until curl -k -s https://"$ARGO_IP" >/dev/null
do
    echo "Waiting for ArgoCD API..."
    sleep 5
done

############################################################
# Login to ArgoCD
############################################################

echo ""
echo "========== Logging into ArgoCD =========="

argocd login \
"$ARGO_IP" \
--username admin \
--password "$ARGO_PASSWORD" \
--insecure

############################################################
# Create Application (only if not exists)
############################################################

echo ""
echo "========== Creating ArgoCD Application =========="

if argocd app get frontend-service >/dev/null 2>&1
then

    echo ""
    echo "Application 'frontend-service' already exists."

else

    argocd app create frontend-service \
    --repo https://github.com/Madheswaran/Projects.git \
    --path devops/paypal-app/helm/frontend-service \
    --dest-server https://kubernetes.default.svc \
    --dest-namespace default \
    --sync-policy automated

    echo ""
    echo "Application Created."

fi

############################################################
# Sync Application
############################################################

echo ""
echo "========== Syncing Application =========="

argocd app sync frontend-service || true

############################################################
# Application Status
############################################################

echo ""
echo "========== Application Status =========="

argocd app get frontend-service

############################################################
# Verify
############################################################

echo ""
echo "========== ArgoCD Applications =========="

argocd app list

echo ""
echo "========== Kubernetes =========="

kubectl get nodes

echo ""

kubectl get pods -A

echo ""

kubectl get svc -A

############################################################
# Azure Summary
############################################################

echo ""
echo "========== Azure Resources =========="

az group list -o table

echo ""

az acr list -o table

echo ""

az aks list -o table

echo ""

az account show --output table

############################################################
# Completed
############################################################

echo ""
echo "======================================================"
echo " PayPal Checkout Platform Bootstrap Completed"
echo "======================================================"
echo ""
echo "ArgoCD URL"
echo ""
echo "https://$ARGO_IP"
echo ""
echo "Username : admin"
echo "Password : $ARGO_PASSWORD"
echo ""
echo "Application : SETUP COMPLETED"
echo ""
echo "======================================================"