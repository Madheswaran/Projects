#!/bin/bash

set -e

echo "==============================================="
echo " PayPal Checkout Platform Bootstrap"
echo "==============================================="




ACR_NAME="acrpaypal$(date +%s)"
AKS_NAME="aks-paypal-dev"
SECRET_NAME="acr-secret"

echo
echo "========== Azure Login =========="
#curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login

echo "Available Resource Groups:"
az group list -o table
RG=$(az group list --query "[0].name" -o tsv)

echo "Using Resource Group: $RG"

echo
echo "========== Creating ACR =========="

if ! az acr show --resource-group "$RG" --name "$ACR_NAME" >/dev/null 2>&1
then
    az acr create \
        --resource-group "$RG" \
        --name "$ACR_NAME" \
        --sku Basic
	az acr list -o table
else
    echo "ACR already exists."
fi

echo
echo "========== Creating AKS =========="

if ! az aks show --resource-group "$RG" --name "$AKS_NAME" >/dev/null 2>&1
then
    az aks create \
        --resource-group "$RG" \
        --name "$AKS_NAME" \
        --node-count 1 \
        --node-vm-size Standard_D2s_v3 \
        --generate-ssh-keys
else
    echo "AKS already exists."
fi



echo
echo "========== Getting AKS Credentials =========="

az aks get-credentials \
    --resource-group "$RG" \
    --name "$AKS_NAME" \
    --overwrite-existing


echo "====================================="
echo "POST AKS SETUP STARTED"
echo "====================================="

############################################
# Get dynamic values
############################################

#RG=$(az group list --query "[0].name" -o tsv)

# AKS_NAME=$(az aks list \
# --resource-group $RG \
# --query "[0].name" \
# -o tsv)

# ACR_NAME=$(az acr list \
# --resource-group $RG \
# --query "[0].name" \
# -o tsv)

ACR_LOGIN_SERVER=$(az acr show \
-n $ACR_NAME \
--query loginServer \
-o tsv)

echo "RG : $RG"
echo "AKS : $AKS_NAME"
echo "ACR : $ACR_NAME"

############################################
# ACR Secret
############################################

echo "Enabling ACR admin"

az acr update \
--name $ACR_NAME \
--admin-enabled true

ACR_USERNAME=$(az acr credential show \
--name $ACR_NAME \
--query username \
-o tsv)

ACR_PASSWORD=$(az acr credential show \
--name $ACR_NAME \
--query passwords[0].value \
-o tsv)

kubectl delete secret acr-secret \
--ignore-not-found

kubectl create secret docker-registry acr-secret \
--docker-server=$ACR_LOGIN_SERVER \
--docker-username=$ACR_USERNAME \
--docker-password=$ACR_PASSWORD

echo "ACR Secret Created"

############################################
# Install Ingress
############################################

echo "Installing Ingress"

helm repo add ingress-nginx \
https://kubernetes.github.io/ingress-nginx

helm repo update

helm upgrade --install ingress-nginx \
ingress-nginx/ingress-nginx \
--namespace ingress-nginx \
--create-namespace

kubectl wait \
--namespace ingress-nginx \
--for=condition=Ready pod \
--selector=app.kubernetes.io/component=controller \
--timeout=300s

kubectl get all -n ingress-nginx

############################################
# Install ArgoCD
############################################

echo "Installing Argo"

helm repo add argo \
https://argoproj.github.io/argo-helm

helm repo update

kubectl create namespace argocd \
--dry-run=client \
-o yaml | kubectl apply -f -

helm upgrade --install argocd \
argo/argo-cd \
-n argocd

helm upgrade argocd \
argo/argo-cd \
-n argocd \
--reuse-values \
--set server.service.type=LoadBalancer

kubectl get all -n argocd

############################################
# Wait for Argo LB
############################################

echo "Waiting for Argo LoadBalancer"

kubectl wait \
--for=jsonpath='{.status.loadBalancer.ingress[0].ip}' \
service/argocd-server \
-n argocd \
--timeout=300s

ARGO_IP=$(kubectl get svc argocd-server \
-n argocd \
-o jsonpath='{.status.loadBalancer.ingress[0].ip}')

echo "ARGO IP : $ARGO_IP"

############################################
# Password
############################################

ARGO_PASSWORD=$(kubectl get secret \
argocd-initial-admin-secret \
-n argocd \
-o jsonpath="{.data.password}" | base64 -d)

echo ""
echo "ARGO USER : admin"
echo "ARGO PASSWORD : $ARGO_PASSWORD"
echo ""

############################################
# Install Argo CLI
############################################

if ! command -v argocd &> /dev/null
then
    curl -sSL \
    -o argocd \
    https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64

    chmod +x argocd

    sudo mv argocd \
    /usr/local/bin/
fi

############################################
# Login
############################################

argocd login \
$ARGO_IP \
--username admin \
--password $ARGO_PASSWORD \
--insecure

############################################
# Create App
############################################

argocd app create paypal-frontend \
--repo https://github.com/Madheswaran/Projects.git \
--path devops/paypal-frontend-app/helm/paypal-frontend \
--dest-server https://kubernetes.default.svc \
--dest-namespace default \
--sync-policy automated \
|| true

############################################
# Verify
############################################

argocd app list

echo ""
echo "ARGO URL"
echo "http://$ARGO_IP"
echo ""

az group list -o table
az acr list -o table
az aks list -o table
az account show

echo "POST AKS SETUP COMPLETED"
