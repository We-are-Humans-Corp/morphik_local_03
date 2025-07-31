# Morphik Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Deployment](#local-development-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Configuration Management](#configuration-management)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Docker 20.10+ and Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 20GB free disk space
- Linux, macOS, or Windows with WSL2

### Required Tools
```bash
# Check Docker version
docker --version
docker compose version

# Check available resources
docker system info
```

## Local Development Deployment

### 1. Clone Repository
```bash
git clone https://github.com/We-are-Humans-Corp/Morphik_local.git
cd Morphik_local
```

### 2. Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
```bash
JWT_SECRET_KEY=your-secret-key-here
POSTGRES_PASSWORD=your-db-password
ANTHROPIC_API_KEY=your-api-key  # Optional for cloud models
```

### 3. Launch Services
```bash
# Start all services
docker compose --profile ollama up -d

# Verify all services are running
docker compose ps

# Check logs
docker compose logs -f
```

### 4. Load Ollama Models
```bash
# Load required models
docker exec -it ollama ollama pull llama3.2:3b
docker exec -it ollama ollama pull nomic-embed-text
```

### 5. Access Application
- Frontend UI: http://localhost:3000
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## Production Deployment

### 1. Security Hardening
```bash
# Generate strong JWT secret
openssl rand -hex 32

# Update production environment
cp .env.production .env
```

### 2. SSL/TLS Configuration
```nginx
# nginx.conf example
server {
    listen 443 ssl http2;
    server_name morphik.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://ui:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://morphik:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Database Backup
```bash
# Backup script
#!/bin/bash
docker exec postgres pg_dump -U morphik morphik_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker exec -i postgres psql -U morphik morphik_db < backup_20250118.sql
```

### 4. Resource Limits
```yaml
# docker-compose.prod.yml
services:
  morphik:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Cloud Deployment Options

### AWS Deployment
```bash
# Using AWS ECS
aws ecs create-cluster --cluster-name morphik-cluster

# Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service --cluster morphik-cluster --service-name morphik-service
```

### Google Cloud Platform
```bash
# Using Google Kubernetes Engine
gcloud container clusters create morphik-cluster --num-nodes=3

# Deploy application
kubectl apply -f kubernetes/

# Expose service
kubectl expose deployment morphik --type=LoadBalancer --port=80
```

### Azure Container Instances
```bash
# Create resource group
az group create --name morphik-rg --location eastus

# Deploy container group
az container create --resource-group morphik-rg --file docker-compose.yml
```

## Configuration Management

### Environment-Specific Configs
```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Staging
docker compose -f docker-compose.yml -f docker-compose.staging.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Secrets Management
```bash
# Using Docker secrets
echo "your-secret" | docker secret create jwt_secret -

# Reference in compose file
secrets:
  jwt_secret:
    external: true
```

## Monitoring and Maintenance

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health

# Monitor logs
docker compose logs -f --tail=100

# Check resource usage
docker stats
```

### Backup Strategy
```bash
# Automated backup script
0 2 * * * /opt/morphik/scripts/backup.sh

# Backup volumes
docker run --rm -v morphik_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### Updates and Upgrades
```bash
# Pull latest changes
git pull origin main

# Rebuild services
docker compose build --no-cache

# Rolling update
docker compose up -d --no-deps --build morphik
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Find processes using ports
lsof -i :3000
lsof -i :8000

# Kill conflicting processes
kill -9 <PID>
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker compose logs postgres

# Test connection
docker exec -it postgres psql -U morphik -d morphik_db -c "SELECT 1;"
```

#### Ollama Model Loading
```bash
# Check Ollama status
docker exec ollama ollama list

# Restart Ollama
docker compose restart ollama
```

#### Memory Issues
```bash
# Check Docker memory usage
docker system df

# Clean up unused resources
docker system prune -a --volumes
```

### Debug Mode
```bash
# Enable debug logging
export DEBUG=true
docker compose up

# Check application logs
docker compose logs morphik | grep ERROR
```

### Performance Optimization
```bash
# Increase PostgreSQL connections
docker exec -it postgres psql -U morphik -c "ALTER SYSTEM SET max_connections = 200;"

# Restart database
docker compose restart postgres
```

## Best Practices

1. **Regular Backups**: Implement automated daily backups
2. **Monitoring**: Set up Prometheus/Grafana for metrics
3. **Security Updates**: Regular dependency updates
4. **Log Rotation**: Configure log rotation to prevent disk fill
5. **Resource Monitoring**: Set up alerts for high resource usage
6. **Documentation**: Keep deployment docs updated
7. **Testing**: Always test in staging before production

## Support and Resources

- GitHub Issues: https://github.com/We-are-Humans-Corp/Morphik_local/issues
- Discord Community: https://discord.gg/morphik
- Documentation: https://morphik.ai/docs
- Email Support: support@morphik.ai