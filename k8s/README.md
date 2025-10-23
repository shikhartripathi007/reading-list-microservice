# Reading List Microservice - Kubernetes Deployment

This directory contains Kubernetes manifests to deploy the reading list microservice.

## 📁 Manifest Files

- `namespace.yaml` - Creates the reading-list namespace
- `postgres-secret.yaml` - Database credentials (base64 encoded)
- `postgres-pvc.yaml` - Persistent volume claim for PostgreSQL data
- `postgres-deployment.yaml` - PostgreSQL database deployment
- `postgres-service.yaml` - PostgreSQL service (ClusterIP)
- `reading-service-deployment.yaml` - Reading service deployment
- `reading-service-service.yaml` - Reading service (LoadBalancer)

## 🚀 Deployment Steps

### 1. Deploy in Order
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Deploy database components
kubectl apply -f k8s/postgres-secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

# Deploy reading service
kubectl apply -f k8s/reading-service-deployment.yaml
kubectl apply -f k8s/reading-service-service.yaml
```

### 2. Deploy All at Once
```bash
kubectl apply -f k8s/
```

## 🔍 Monitoring

### Check Deployment Status
```bash
kubectl get all -n reading-list
kubectl get pv,pvc -n reading-list
```

### Check Pod Logs
```bash
kubectl logs -f deployment/postgres-deployment -n reading-list
kubectl logs -f deployment/reading-service-deployment -n reading-list
```

### Access the Service
```bash
# Get service URL (for LoadBalancer)
kubectl get svc reading-service -n reading-list

# Port forward for local testing
kubectl port-forward svc/reading-service 8080:80 -n reading-list
```

## 🔧 Configuration Notes

### Storage Class
Update `storageClassName` in `postgres-pvc.yaml` based on your cluster:
- **GKE**: `standard-rwo` or `premium-rwo`
- **EKS**: `gp2` or `gp3`
- **AKS**: `default` or `managed-premium`
- **Local/Minikube**: `standard`

### Service Type
The reading service uses `LoadBalancer` type. For local clusters, consider:
- Change to `NodePort` for minikube/kind
- Use `ClusterIP` + Ingress for production

### Health Checks
Both services include liveness and readiness probes. Ensure your Flask app has:
- `/health` endpoint for health checks
- Proper startup time configuration

## 🧹 Cleanup
```bash
kubectl delete namespace reading-list
```

This will remove all resources in the namespace.