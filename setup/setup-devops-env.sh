#!/bin/bash

set -e

echo "=================================================="
echo "Updating Ubuntu"
echo "=================================================="

sudo apt update
sudo apt upgrade -y

echo "=================================================="
echo "Installing Common Packages"
echo "=================================================="

sudo apt install -y \
curl \
wget \
git \
vim \
nano \
tree \
htop \
btop \
jq \
zip \
unzip \
tmux \
ca-certificates \
gnupg \
lsb-release \
software-properties-common \
build-essential \
python3 \
python3-pip \
python3-venv

echo "=================================================="
echo "Creating Workspace"
echo "=================================================="

mkdir -p ~/workspace/{cpp,devops,devops_scripts,setup}

###########################################################
# GIT CONFIGURATION
###########################################################

echo "=================================================="
echo "Configuring Git"
echo "=================================================="

read -p "Git User Name: " GIT_NAME
read -p "Git Email: " GIT_EMAIL

git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
git config --global init.defaultBranch main

###########################################################
# SSH KEY
###########################################################

echo "=================================================="
echo "Generating SSH Key"
echo "=================================================="

mkdir -p ~/.ssh

if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "$GIT_EMAIL"
fi

echo ""
echo "=================================================="
echo "GitHub Public Key"
echo "=================================================="

cat ~/.ssh/id_ed25519.pub

echo ""
echo "Add above key into:"
echo "GitHub -> Settings -> SSH and GPG Keys"

###########################################################
# KUBECTL
###########################################################

echo "=================================================="
echo "Installing kubectl"
echo "=================================================="

curl -LO "https://dl.k8s.io/release/$(curl -L -s \
https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

sudo install -o root -g root -m 0755 \
kubectl /usr/local/bin/kubectl

rm kubectl

###########################################################
# HELM
###########################################################

echo "=================================================="
echo "Installing Helm"
echo "=================================================="

curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

###########################################################
# TERRAFORM
###########################################################

echo "=================================================="
echo "Installing Terraform"
echo "=================================================="

wget -O- https://apt.releases.hashicorp.com/gpg | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg >/dev/null

echo \
"deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] \
https://apt.releases.hashicorp.com noble main" | \
sudo tee /etc/apt/sources.list.d/hashicorp.list

sudo apt update
sudo apt install terraform -y

###########################################################
# DOCKER
###########################################################

echo "=================================================="
echo "Installing Docker Engine"
echo "=================================================="

sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor \
-o /etc/apt/keyrings/docker.gpg

echo \
"deb [arch=$(dpkg --print-architecture) \
signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu noble stable" | \
sudo tee /etc/apt/sources.list.d/docker.list

sudo apt update

sudo apt install -y \
docker-ce \
docker-ce-cli \
containerd.io \
docker-buildx-plugin \
docker-compose-plugin

sudo usermod -aG docker $USER

###########################################################
# AZURE CLI
###########################################################

echo "=================================================="
echo "Installing Azure CLI"
echo "=================================================="

curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

###########################################################
# TRIVY
###########################################################

echo "=================================================="
echo "Installing Trivy"
echo "=================================================="

wget -qO - \
https://aquasecurity.github.io/trivy-repo/deb/public.key | \
gpg --dearmor | \
sudo tee /usr/share/keyrings/trivy.gpg >/dev/null

echo \
"deb [signed-by=/usr/share/keyrings/trivy.gpg] \
https://aquasecurity.github.io/trivy-repo/deb noble main" | \
sudo tee /etc/apt/sources.list.d/trivy.list

sudo apt update
sudo apt install trivy -y

###########################################################
# SONAR SCANNER
###########################################################

echo "=================================================="
echo "Installing Sonar Scanner"
echo "=================================================="

cd /tmp

wget \
https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-7.2.0.5079-linux-x64.zip

unzip sonar-scanner-*.zip

sudo mv sonar-scanner-* /opt/sonar-scanner

echo '' >> ~/.bashrc
echo '# Sonar Scanner' >> ~/.bashrc
echo 'export PATH=$PATH:/opt/sonar-scanner/bin' >> ~/.bashrc

export PATH=$PATH:/opt/sonar-scanner/bin

###########################################################
# kubectx / kubens
###########################################################

echo "=================================================="
echo "Installing kubectx / kubens"
echo "=================================================="

sudo git clone \
https://github.com/ahmetb/kubectx \
/opt/kubectx || true

sudo ln -sf \
/opt/kubectx/kubectx \
/usr/local/bin/kubectx

sudo ln -sf \
/opt/kubectx/kubens \
/usr/local/bin/kubens

###########################################################
# K9S
###########################################################

echo "=================================================="
echo "Installing k9s"
echo "=================================================="

cd /tmp

wget -O k9s.deb \
https://github.com/derailed/k9s/releases/latest/download/k9s_linux_amd64.deb

sudo apt install ./k9s.deb -y

###########################################################
# BASH CUSTOMIZATION
###########################################################

echo "=================================================="
echo "Updating .bashrc"
echo "=================================================="

cat <<'EOF' >> ~/.bashrc

#############################################
# Custom Prompt
#############################################

PS1='\[\e[1;32m\]\u:\W\$ \[\e[0m\]'

#############################################
# Aliases
#############################################

alias cls='clear'
alias ll='ls -ltr'
alias gs='git status'
alias gp='git push'
alias k='kubectl'
alias d='docker'
alias tf='terraform'

#############################################
# Welcome Message
#############################################

echo ""
echo "=========================================="
echo " Welcome Madhes 🚀"
echo " DevOps + C++ Workspace Ready"
echo "=========================================="
echo ""

EOF

###########################################################
# VERSIONS
###########################################################

echo ""
echo "=================================================="
echo "Installed Versions"
echo "=================================================="

git --version
docker --version
kubectl version --client
helm version
terraform version
az version | head
trivy --version
sonar-scanner --version

echo ""
echo "=================================================="
echo "SETUP COMPLETED"
echo "=================================================="
echo ""
echo "Run:"
echo ""
echo "exit"
echo ""
echo "Then from PowerShell:"
echo ""
echo "wsl --shutdown"
echo ""
echo "Open Ubuntu again."
echo ""
