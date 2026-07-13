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


echo "ACR Username: $ACR_USERNAME"
echo "Bootstrap completed successfully."
