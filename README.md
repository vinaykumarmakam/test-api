# test-api

Micro-SaaS data product built on briggon-dataplatform.

## Quick Start

```bash
# Build locally
docker build -t test-api:latest .

# Run locally
docker run -p 8000:8000 test-api:latest

# Access API
curl http://localhost:8000/health
```

## Deploy to Kubernetes

```bash
# Option 1: Helm (manual)
helm install test-api ./helm-chart -n products --create-namespace

# Option 2: ArgoCD (GitOps - recommended)
kubectl apply -f argocd-application.yaml
# ArgoCD will auto-deploy on git push
```

## API Endpoints

- `GET /` - Service info
- `GET /health` - Health check
- `GET /ready` - Readiness probe
- `POST /api/v1/process` - Submit data processing job
- `GET /api/v1/job/{job_id}` - Get job status
- `GET /metrics` - Prometheus metrics

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn src.api:app --reload

# Run tests
pytest tests/ -v

# Run worker
celery -A src.worker worker --loglevel=info
```

## Production URL

**https://test-api.briggon.ai**

## Monitoring

- Grafana: https://grafana.briggon.ai
- Tekton: https://tekton.briggon.ai
- ArgoCD: https://argocd.briggon.ai

## Configuration

Edit `helm-chart/values.yaml`:
- Image repository
- Resource limits
- Environment variables
- Autoscaling thresholds

## CI/CD Pipeline

Push to `main` branch triggers:
1. Run tests
2. Build Docker image
3. Push to registry
4. ArgoCD auto-deploys
5. Available at https://test-api.briggon.ai in ~2 minutes

## Structure

```
test-api/
├── src/           # Application code
├── tests/         # Test suite
├── helm-chart/    # Kubernetes deployment
├── tekton/        # CI/CD pipeline
└── Dockerfile     # Container image
```
