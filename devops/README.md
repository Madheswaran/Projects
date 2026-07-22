# PayPal Checkout – DevOps GitOps Project

## Project Overview

This project demonstrates an end-to-end DevOps implementation using:

- Azure Kubernetes Service (AKS)
- Azure Container Registry (ACR)
- GitHub Actions CI/CD
- Helm
- ArgoCD GitOps
- Kubernetes Ingress
- Horizontal Pod Autoscaler (HPA)
- Health Probes
- Failure Recovery
- Service-to-Service Communication
- Taints and Tolerations

---

# High Level Architecture

Developer
    |
    | Git Push
    ↓
GitHub Repository
    |
    ↓
GitHub Actions Pipeline
    |
    ├── Unit Testing
    ├── Docker Build
    ├── Trivy Security Scan
    ├── Push Images to ACR
    ├── Update Helm values.yaml
    └── Commit Image Tag
                |
                ↓
           Git Repository
                |
                ↓
             ArgoCD
                |
                ↓
         Helm Template
                |
                ↓
       Kubernetes API Server
                |
                ↓
        Deployment Controller
                |
                ↓
      ReplicaSets → Pods


# Application Network Flow

Internet User
      |
      ↓
Azure Load Balancer (NLB)
      |
      ↓
NGINX Ingress Controller
      |
      ↓
Ingress Rules
      |
      ↓
Frontend Service (ClusterIP)
      |
      ↓
Frontend Pods
      |
      ↓
User Service (ClusterIP)
      |
      ↓
User Pods

---

# Components Used

## Azure Components

- Azure Kubernetes Service (AKS)
- Azure Container Registry (ACR)
- Azure Load Balancer (Automatically created)

---

## Kubernetes Components

### Workloads

- Deployment
- ReplicaSet
- Pods

### Networking

- Service (ClusterIP)
- Kubernetes DNS
- Ingress
- NGINX Ingress Controller

### Configuration

- ConfigMap
- Secret

### Health Checks

- Readiness Probe
- Liveness Probe

### Autoscaling

- Horizontal Pod Autoscaler (HPA)

### Scheduling

- Taints
- Tolerations

### GitOps

- ArgoCD
- Helm

---

# CI/CD Workflow

## 1. Developer Pushes Code

```bash
git push origin main
```

---

## 2. GitHub Actions Pipeline

Pipeline Stages:

### Stage 1

Checkout Source Code

### Stage 2

Install Dependencies

### Stage 3

Run Unit Tests

### Stage 4

Run Trivy Security Scan

### Stage 5

Build Docker Images

```text
frontend-service:<github.sha>
user-service:<github.sha>
```

### Stage 6

Push Docker Images to ACR

### Stage 7

Update Helm values.yaml

```yaml
image:
  repository:
  tag:
```

### Stage 8

Commit Updated Image Tag

Purpose:

ArgoCD detects Git change and starts deployment.

---

# GitOps Deployment Flow

```text
Git Change
      ↓
ArgoCD detects drift
      ↓
helm template
      ↓
kubectl apply
      ↓
Deployment Updated
      ↓
ReplicaSet Created
      ↓
Pods Created
```

---

# Kubernetes Deployment Flow

```text
Deployment
      ↓
ReplicaSet
      ↓
Pods
```

Deployment Controller performs rolling updates automatically.

---

# Service-to-Service Communication

Frontend communicates with User Service using Kubernetes DNS.

Example:

```python
requests.get(
    "http://user-service/users"
)
```

No Pod IP is required.

---

# Features Implemented

---

## 1. Rolling Deployment

Changing Deployment spec automatically creates:

```text
New ReplicaSet
      ↓
New Pods
      ↓
Old Pods Terminated
```

---

## 2. Readiness Probe

Endpoint:

```python
/ready
```

Scenario Tested:

```python
return "NOT READY",500
```

Result:

- Pod remains Running
- Traffic not routed to pod

---

## 3. Liveness Probe

Endpoint:

```python
/health
```

Scenario Tested:

```python
return "DOWN",500
```

Result:

Container restarts automatically.

---

## 4. Service-to-Service Communication

Tested:

Frontend Pod → User Service

Verified:

- Kubernetes DNS
- Cluster Networking

---

## 5. Failure Recovery

Deleted Deployment manually.

Scenario:

```bash
kubectl delete deployment frontend-service
```

Result:

ArgoCD redeployed application from Git desired state.

---

## 6. Horizontal Pod Autoscaler (HPA)

Configured:

```yaml
minReplicas: 1
maxReplicas: 5
targetCPUUtilizationPercentage: 50
```

Load Generation:

```bash
while true; do
  wget -q -O- http://frontend-service
done
```

Observed:

```text
1 Pod
 ↓
5 Pods
 ↓
1 Pod
```

Automatic scale-down occurred after CPU usage reduced.

---

## 7. Taints and Tolerations

Applied:

```bash
kubectl taint node NODE frontend=true:NoSchedule
```

Observed:

- Existing Pods remained.
- New Pods could not schedule.

Purpose:

Reserve nodes for specific workloads.

---

## 8. OOM Scenario

Reduced Memory Limits:

```yaml
memory: 10Mi
```

Observed:

```text
OOMKilled
CrashLoopBackOff
```

Recovery:

Updated Deployment and resynced through ArgoCD.

---

# Current Project Structure

```text
Projects
│
├── frontend-service
│
├── user-service
│
├── helm
│     ├── frontend-service
│     └── user-service
│
├── github workflows
│     ├── frontend pipeline
│     └── user pipeline
│
└── argocd manifests
```

---

# Technologies Used

| Category | Tools |
|-----------|--------|
| Cloud | Azure |
| Container | Docker |
| Orchestration | Kubernetes |
| CI/CD | GitHub Actions |
| GitOps | ArgoCD |
| Packaging | Helm |
| Security | Trivy |
| Registry | ACR |
| Language | Python Flask |

---

# Future Enhancements

Planned Improvements:

- Vertical Pod Autoscaler (VPA)
- Network Policies
- Sidecar Containers
- Pod Disruption Budget (PDB)
- Canary Deployment
- Blue Green Deployment
- Prometheus Monitoring
- Grafana Dashboards
- Loki Logging
- Argo Rollouts
- Multi-Environment GitOps
- Multi-Cluster AKS
- Service Mesh (Istio)

---