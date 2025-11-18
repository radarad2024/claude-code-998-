# Deployment Guide

## 🚀 Quick Start with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB+ RAM recommended
- NVIDIA GPU (optional, for faster AI inference)

### Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-radiologist-assistant
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Start services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Production Deployment

#### 1. Update Environment Variables

Edit `.env` for production:
```bash
SECRET_KEY=<generate-strong-secret-key>
DATABASE_URL=<your-production-database>
ALLOWED_ORIGINS=https://yourdomain.com
ENABLE_AUDIT_LOG=true
ENCRYPTION_AT_REST=true
```

#### 2. Build Production Images

```bash
docker-compose -f docker-compose.prod.yml build
```

#### 3. Run Production Stack

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Manual Installation

### Backend Setup

```bash
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
npm run preview
```

## 🗄️ Database Setup

### PostgreSQL

```bash
# Create database
createdb radiologist_db

# Run migrations
cd backend
alembic upgrade head
```

### SQLite (Development Only)

Database will be created automatically at `backend/radiologist_assistant.db`

## 🔐 Security Configuration

### Generate Secret Key

```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(secret_key)
```

### SSL/TLS Configuration

For production, use a reverse proxy (nginx) with SSL:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📊 Model Deployment

### Download Pre-trained Models

```bash
# Create model directory
mkdir -p backend/model_weights

# Download models (example)
cd backend/model_weights

# Chest X-ray models
wget https://example.com/models/chest_xray_ensemble.pth

# Brain CT models
wget https://example.com/models/brain_ct_hemorrhage.pth

# Bone fracture models
wget https://example.com/models/bone_fracture_detector.pth
```

### GPU Support

For GPU-accelerated inference:

```dockerfile
# Update backend/Dockerfile
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Install PyTorch with CUDA
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

Update docker-compose.yml:
```yaml
backend:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

## 🔍 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connectivity
curl http://localhost:8000/api/v1/health/db
```

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Application logs
tail -f backend/radiologist_assistant.log
```

## 📈 Scaling

### Horizontal Scaling

Use Kubernetes for production:

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: radiologist-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: radiologist-backend
  template:
    metadata:
      labels:
        app: radiologist-backend
    spec:
      containers:
      - name: backend
        image: radiologist-backend:latest
        ports:
        - containerPort: 8000
```

### Load Balancing

Use nginx or HAProxy for load balancing:

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}
```

## 🔄 Backup & Recovery

### Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U radiologist radiologist_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U radiologist radiologist_db < backup.sql
```

### Model Weights Backup

```bash
# Backup
tar -czf model_weights_backup.tar.gz backend/model_weights/

# Restore
tar -xzf model_weights_backup.tar.gz -C backend/
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
./scripts/integration_tests.sh
```

## 📝 Maintenance

### Update Dependencies

```bash
# Backend
pip install -r requirements.txt --upgrade

# Frontend
npm update
```

### Database Migrations

```bash
cd backend

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
```

2. **Database connection error**
```bash
# Check PostgreSQL status
docker-compose ps postgres
docker-compose logs postgres
```

3. **GPU not detected**
```bash
# Check NVIDIA driver
nvidia-smi

# Install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
```

## 📞 Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/wiki
