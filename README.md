# ⚡ Proactive Autoscaling for Microservices on Kubernetes

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/Argo%20CD-1e0b3e?style=for-the-badge&logo=argo&logoColor=#d16044)
![Grafana](https://img.shields.io/badge/Grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=Prometheus&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Ansible](https://img.shields.io/badge/ansible-%231A1918.svg?style=for-the-badge&logo=ansible&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

## 📖 Project Overview

This project implements a **Proactive Autoscaling Platform** for microservices deployed on a K3s Kubernetes cluster. Unlike traditional reactive scaling (HPA) that responds *after* traffic spikes, this system uses an **AI-powered Prophet model** to **predict future traffic** and scale services *before* demand increases.

The entire platform is managed through **GitOps (ArgoCD)** and provisioned via **Ansible automation**, enabling full cluster bootstrap from bare metal to a production-ready state in a single command.

### Key Highlights
- 🤖 **AI-Driven Proactive Scaling** — KEDA polls a FastAPI prediction endpoint to pre-scale services before traffic spikes occur
- 🔄 **GitOps (ArgoCD App-of-Apps)** — Single bootstrap point for the entire infrastructure with automated synchronization
- 🔐 **DevSecOps Pipeline** — GitHub Actions with Trivy vulnerability scanning, yamllint, kubeconform, and Flake8
- 🔑 **Zero Plaintext Secrets** — Bitnami Sealed Secrets with automated certificate retrieval and encryption via Ansible
- 📊 **Full Observability** — kube-prometheus-stack with custom Traefik ServiceMonitor for RPS metrics

## 🏗️ Architecture

<!-- Replace this section with your draw.io diagram -->
<!-- See the mermaid diagram below for reference -->

```mermaid
graph TB
    subgraph "Developer Workstation"
        DEV[Developer Push]
    end

    subgraph "GitHub"
        REPO[Git Repository]
        subgraph "GitHub Actions CI"
            LINT[yamllint + Flake8 + Kubeconform]
            BUILD[Docker Build]
            TRIVY[Trivy Vulnerability Scan]
            PUSH[Push to GHCR]
            TAG[Update Manifest Tag]
        end
    end

    subgraph "K3s Cluster"
        subgraph "GitOps Layer"
            ARGO[ArgoCD]
            AOAPPS["App-of-Apps (Root)"]
        end

        subgraph "Application Layer — namespace: boutique"
            FRONT[Frontend]
            CART[Cart Service]
            CHECKOUT[Checkout Service]
            PRODUCT[Product Catalog]
            CURRENCY[Currency Service]
            SHIPPING[Shipping Service]
            PAYMENT[Payment Service]
            EMAIL[Email Service]
            REDIS[Redis]
            LOADGEN[Load Generator]
        end

        subgraph "AI Scaling Layer — namespace: boutique"
            AI[AI Server - FastAPI]
            MODEL["Prophet Model (Fixed)"]
            MLFLOW[MLflow Tracking Server]
            INGEST[Data Ingestion CronJob]
            RETRAIN[Model Retrain CronJob]
            PVC[Shared PVC Storage]
        end

        subgraph "Scaling Engine"
            KEDA[KEDA]
            SCALEOBJ["ScaledObjects (8 services)"]
        end

        subgraph "Observability — namespace: monitoring"
            PROM[Prometheus]
            GRAFANA[Grafana]
            TRAEFIK_MON[Traefik ServiceMonitor]
        end

        subgraph "Security — namespace: kube-system"
            SEALED[Sealed Secrets Controller]
        end

        subgraph "Ingress — namespace: kube-system"
            TRAEFIK[Traefik Ingress]
        end
    end

    DEV --> REPO
    REPO --> LINT --> BUILD --> TRIVY --> PUSH --> TAG
    TAG -->|update image SHA| REPO
    REPO -->|watch & sync| ARGO
    ARGO --> AOAPPS
    AOAPPS -->|sync| FRONT & AI & PROM & KEDA & SEALED & TRAEFIK

    KEDA -->|poll /api/forecast| AI
    AI --> MODEL
    KEDA -->|scale| SCALEOBJ
    SCALEOBJ -->|adjust replicas| FRONT & CART & CHECKOUT & PRODUCT

    TRAEFIK -->|expose metrics| TRAEFIK_MON
    TRAEFIK_MON -->|scrape| PROM
    PROM -->|query| INGEST
    INGEST -->|store data| PVC
    RETRAIN -->|read data| PVC
    RETRAIN -->|push model| MLFLOW

    GRAFANA -->|visualize| PROM
```

> **Note:** This Mermaid diagram is a reference for the system architecture. For the final report, recreate this in [draw.io](https://draw.io) for a cleaner presentation.

## 📂 Repository Structure

```text
├── .github/workflows/
│   ├── ci-ai-scaler.yml        # CI: Build → Trivy Scan → Push → Update Tag
│   └── audit-ci.yaml           # Audit: yamllint + Flake8 + Kubeconform
├── apps/
│   ├── boutique/
│   │   └── google_boutique.yaml # Google Online Boutique microservices (8 services)
│   └── prophet/
│       ├── Dockerfile           # Non-root Python container
│       ├── ai_server.py         # FastAPI prediction endpoint (/api/forecast)
│       ├── data_ingestion.py    # Daily Prometheus → CSV data pipeline
│       ├── model_retrain.py     # Weekly sliding window retraining
│       ├── ai-scaler-architecture.yaml  # CronJobs + Deployment + Service
│       ├── ai-configmap.yaml    # Environment configuration
│       ├── mlflow-server.yaml   # MLflow Tracking Server
│       ├── ghcr_sealed.yaml     # Encrypted GHCR registry credentials
│       └── prophet_model/       # Baked-in Prophet model artifact
├── infra/
│   ├── ansible/
│   │   ├── playbook.yaml        # End-to-end cluster provisioning (5 steps)
│   │   ├── hosts.ini            # Inventory (master + worker)
│   │   └── ansible.cfg
│   ├── argocd/
│   │   ├── argocd-app.yaml      # App-of-Apps root application
│   │   ├── boutique-app.yaml    # Boutique microservices (with ignoreDifferences)
│   │   ├── prophet-app.yaml     # AI scaler components
│   │   ├── monitoring-app.yaml  # kube-prometheus-stack (Helm)
│   │   ├── keda-app.yaml        # KEDA ScaledObjects
│   │   ├── ingress-app.yaml     # Traefik Ingress rules
│   │   └── sealed-secrets-app.yaml  # Sealed Secrets controller (Helm)
│   ├── autoscaling/
│   │   └── keda_hpa.yaml        # 8 ScaledObjects (1 proactive + 7 reactive)
│   ├── monitoring/
│   │   └── values.yaml          # Grafana + Prometheus custom values
│   └── ingress/
│       ├── boutique-ingress.yaml       # web.local, api.local, mlflow.local
│       ├── monitoring-ingress.yaml     # grafana.local
│       ├── argocd-ingress.yaml         # argocd.local
│       └── traefik-metrics-config.yaml # ServiceMonitor for Traefik RPS
└── load-test/
    └── quick_test.py            # Locust load testing script
```

## ⚙️ Quick Start — Full Cluster Bootstrap

### Prerequisites
- 2 Ubuntu VMs (Master: 8GB RAM, Worker: 2GB RAM) with SSH access
- Ansible installed on your control machine
- GitHub account with a PAT token for GHCR access

### 1. Configure Inventory

Edit `infra/ansible/hosts.ini` with your VM IPs:
```ini
[master]
<MASTER_IP> ansible_user=<USER> ansible_ssh_private_key_file=~/.ssh/id_rsa

[worker]
<WORKER_IP> ansible_user=<USER> ansible_ssh_private_key_file=~/.ssh/id_rsa
```

### 2. Run the Playbook

```bash
cd infra/ansible
ansible-playbook playbook.yaml
```

The playbook will:
1. Install base packages on all nodes
2. Provision K3s control plane + install kubeseal CLI
3. Join worker node to the cluster
4. Install KEDA + ArgoCD + Apply App-of-Apps
5. Prompt for GHCR token & Grafana password → auto-seal and apply

### 3. Verify Deployment

```bash
# Check ArgoCD applications
k3s kubectl get applications -n argocd

# Check all pods
k3s kubectl get pods -A

# Access services (add to /etc/hosts)
# <MASTER_IP> web.local grafana.local argocd.local api.local mlflow.local
```

## 🤖 How Proactive Scaling Works

```
1. Traefik receives traffic → exposes RPS metrics
2. Prometheus scrapes Traefik metrics via ServiceMonitor
3. Data Ingestion CronJob (daily) → queries Prometheus → appends to CSV
4. Model Retrain CronJob (weekly) → trains Prophet on sliding window → pushes to MLflow
5. AI Server loads Prophet model → exposes GET /api/forecast → returns predicted RPS
6. KEDA polls /api/forecast every 30s → scales frontend BEFORE traffic arrives
7. Other services use CPU-based reactive scaling as fallback
```

> **Design Decision:** The AI server uses a fixed model trained on synthetic (mock) data for demo stability. The retrain pipeline exists to demonstrate the complete MLOps architecture, but real Prometheus data lacks sufficient seasonality for accurate predictions in a lab environment.

## 🔐 Security Design

| Layer | Implementation |
|-------|---------------|
| **Container Registry** | Sealed Secret (`ghcr_sealed.yaml`) — asymmetric encryption |
| **Grafana Admin** | Sealed Secret via Ansible `vars_prompt` — no plaintext in Git |
| **Container Runtime** | Non-root user (UID 1000) + Pod `securityContext` |
| **CI Pipeline** | Trivy scan blocks CRITICAL/HIGH vulnerabilities |
| **Code Quality** | Flake8 (Python) + yamllint (YAML) + Kubeconform (K8s schemas) |

## 🔄 CI/CD Pipeline

```
Push to apps/prophet/** on main
    │
    ├── Build Docker Image (Buildx + GHA layer cache)
    ├── Trivy Vulnerability Scan (block on CRITICAL/HIGH)
    ├── Push to GitHub Container Registry
    └── Update image tag in ai-scaler-architecture.yaml (git commit + push)
            │
            └── ArgoCD detects change → auto-sync → rolling update
```

## 📊 Monitoring Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Boutique Shop | `http://web.local` | — |
| Grafana | `http://grafana.local` | Set during playbook run |
| ArgoCD | `http://argocd.local` | `admin` / `kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' \| base64 -d` |
| AI Forecast API | `http://api.local/api/forecast` | — |
| MLflow | `http://mlflow.local` | — |

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Orchestration** | K3s (lightweight Kubernetes) |
| **GitOps** | ArgoCD (App-of-Apps pattern) |
| **Autoscaling** | KEDA (metrics-api + CPU triggers) |
| **AI/ML** | Facebook Prophet, MLflow, FastAPI |
| **CI/CD** | GitHub Actions, Docker Buildx, Trivy |
| **Monitoring** | Prometheus, Grafana, Traefik ServiceMonitor |
| **Security** | Bitnami Sealed Secrets, kubeseal |
| **IaC** | Ansible |
| **Ingress** | Traefik (K3s default) |
| **Load Testing** | Locust |

## 📝 Known Limitations

- **Single-environment:** No dev/staging separation (lab scope)
- **No TLS:** `.local` domains use HTTP only (would use cert-manager + Let's Encrypt in production)
- **No alerting rules:** Prometheus collects metrics but no PrometheusRule CRDs for alerts
- **No NetworkPolicy:** All pods can communicate freely within the cluster
- **Fixed AI model:** Production would implement automated model promotion from MLflow

---

*This project was developed as a Major Project (Đồ án chuyên ngành) focusing on DevOps Engineering practices.*
