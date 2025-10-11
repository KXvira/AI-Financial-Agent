# 🚀 AI Financial Agent - Deployment Guide

## Quick Start: Production Deployment

This guide will help you deploy the AI Financial Agent to production in **under 10 minutes**.

---

## 📋 Prerequisites

### Required Software
- [x] Docker (20.10+)
- [x] Docker Compose (2.0+)
- [x] Git

### Required Credentials
- [x] Google Gemini API Key
- [x] MongoDB Atlas connection string (or local MongoDB)
- [x] Domain name (optional, can use IP)
- [x] SSL certificate (optional, can use Let's Encrypt)

---

## 🎯 Deployment Options

### Option 1: Quick Local Testing (5 minutes)

Perfect for testing before production deployment.

```bash
# 1. Clone repository
git clone <your-repo-url>
cd AI-Financial-Agent

# 2. Create environment file
cat > .env.production << EOF
APP_ENV=production
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=ai_financial_agent

GEMINI_API_KEY=your-gemini-api-key-here

REDIS_URL=redis://redis:6379/0

PROMETHEUS_ENABLED=true
EOF

# 3. Make deploy script executable
chmod +x deploy.sh

# 4. Deploy!
./deploy.sh

# 5. Test the deployment
curl http://localhost/api/ocr/health
```

**Access Points:**
- API: http://localhost/api
- Swagger Docs: http://localhost/docs
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090

### Option 2: Full Production Deployment (10 minutes)

Complete production deployment with SSL and domain.

#### Step 1: Server Setup

```bash
# SSH into your production server
ssh user@your-server.com

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### Step 2: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd AI-Financial-Agent

# Create production environment file
nano .env.production
```

**Copy this template:**

```env
# ==========================================
# AI Financial Agent - Production Config
# ==========================================

# Application
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key-min-32-chars-use-openssl-rand-hex-32
APP_HOST=0.0.0.0
APP_PORT=8000

# JWT Authentication
JWT_SECRET_KEY=your-jwt-secret-key-min-32-chars-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7

# MongoDB Atlas
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ai_financial_agent

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key-from-google-ai-studio

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=your-redis-password

# API Configuration
API_V1_PREFIX=/api
MAX_UPLOAD_SIZE=26214400  # 25MB
RATE_LIMIT_PER_MINUTE=60
OCR_TIMEOUT=600

# CORS Origins (comma-separated)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_ENABLED=true

# Nginx
DOMAIN_NAME=yourdomain.com
SSL_CERT_EMAIL=your-email@example.com
```

**Generate secure keys:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

#### Step 3: SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

Update `docker-compose.production.yml` nginx volumes:
```yaml
nginx:
  volumes:
    - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    - /etc/letsencrypt:/etc/letsencrypt:ro  # Add this line
```

#### Step 4: Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh

# Follow the prompts and verify each step
```

#### Step 5: Verify Deployment

```bash
# Check all services are running
docker-compose -f docker-compose.production.yml ps

# Test health endpoint
curl https://yourdomain.com/api/ocr/health

# Test authentication
curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo123"}'

# View logs if needed
docker-compose -f docker-compose.production.yml logs -f backend
```

---

## 🔐 Security Checklist

Before going live, ensure:

- [ ] Changed all default passwords
- [ ] Generated strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configured proper CORS_ORIGINS
- [ ] SSL certificate installed and working
- [ ] Firewall configured (ports 80, 443 only)
- [ ] MongoDB authentication enabled
- [ ] Redis password set
- [ ] Rate limiting configured
- [ ] Backup strategy in place
- [ ] Monitoring alerts configured

---

## 📊 Post-Deployment

### 1. Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | https://yourdomain.com/docs | None |
| Grafana | https://yourdomain.com:3000 | admin/admin (change!) |
| Prometheus | https://yourdomain.com:9090 | None |

### 2. Create Admin User

```bash
# Using the API
curl -X POST https://yourdomain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@yourdomain.com",
    "password": "YourSecurePassword123!"
  }'
```

### 3. Test OCR Processing

```bash
# Get authentication token
TOKEN=$(curl -X POST https://yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YourPassword"}' \
  | jq -r '.access_token')

# Upload receipt for processing
curl -X POST https://yourdomain.com/api/ocr/process \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@path/to/receipt.jpg"
```

### 4. Monitor Performance

Visit Grafana dashboard:
1. Open https://yourdomain.com:3000
2. Login (admin/admin)
3. Navigate to Dashboards → Application Overview
4. Monitor request rates, latencies, errors

---

## 🔄 Continuous Deployment

### GitHub Actions Setup

1. **Add Repository Secrets**

Go to GitHub repo → Settings → Secrets → New repository secret:

```
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
PRODUCTION_HOST=your-server.com
PRODUCTION_USER=ubuntu
SSH_PRIVATE_KEY=<paste your private SSH key>
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

2. **Deploy on Push**

The CI/CD pipeline will automatically:
- Run tests on every push
- Build Docker images
- Deploy to production on main branch
- Send notifications to Slack

3. **Manual Deployment**

```bash
# From GitHub Actions tab
Actions → Deploy to Production → Run workflow
```

---

## 🛠️ Common Tasks

### Update Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.production.yml up -d --build

# Verify health
curl https://yourdomain.com/api/ocr/health
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.production.yml logs -f

# Specific service
docker-compose -f docker-compose.production.yml logs -f backend

# Last 100 lines
docker-compose -f docker-compose.production.yml logs --tail=100 backend
```

### Database Backup

```bash
# Backup MongoDB
docker-compose -f docker-compose.production.yml exec mongodb \
  mongodump --out /data/backup

# Copy to host
docker cp <container-id>:/data/backup ./mongodb-backup-$(date +%Y%m%d)
```

### Scale Services

```bash
# Scale Celery workers
docker-compose -f docker-compose.production.yml up -d --scale celery-worker=3

# Scale backend (requires load balancer)
docker-compose -f docker-compose.production.yml up -d --scale backend=3
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.production.yml restart

# Restart specific service
docker-compose -f docker-compose.production.yml restart backend

# Graceful reload (no downtime)
docker-compose -f docker-compose.production.yml up -d --no-deps --build backend
```

---

## 🚨 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Check environment variables
docker-compose -f docker-compose.production.yml config

# Rebuild from scratch
docker-compose -f docker-compose.production.yml down -v
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Set memory limits in docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Database Connection Issues

```bash
# Check MongoDB is running
docker-compose -f docker-compose.production.yml ps mongodb

# Test connection
docker-compose -f docker-compose.production.yml exec backend \
  python -c "from motor.motor_asyncio import AsyncIOMotorClient; \
  import asyncio; \
  async def test(): \
    client = AsyncIOMotorClient('mongodb://mongodb:27017'); \
    print(await client.server_info()); \
  asyncio.run(test())"
```

### SSL Certificate Renewal

```bash
# Certbot auto-renewal is set up by default
# Manual renewal:
sudo certbot renew

# Restart Nginx after renewal
docker-compose -f docker-compose.production.yml restart nginx
```

---

## 📈 Performance Tuning

### 1. Optimize Docker Images

```bash
# Multi-stage build reduces image size
# Already implemented in Dockerfile.production

# Check image size
docker images | grep ai-financial-agent
```

### 2. Configure Gunicorn Workers

In `Dockerfile.production`:
```dockerfile
# Adjust workers based on CPU cores
# Formula: (2 x CPU cores) + 1
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 3. Redis Cache Tuning

In `.env.production`:
```env
# Increase cache size
REDIS_MAXMEMORY=512mb
REDIS_MAXMEMORY_POLICY=allkeys-lru
```

### 4. Database Indexing

```python
# Add indexes for frequent queries
await db.ocr_results.create_index("task_id")
await db.ocr_results.create_index("timestamp")
await db.receipts.create_index("user_id")
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

```bash
# Never commit .env files
echo ".env.production" >> .gitignore

# Use secrets management in production
# AWS Secrets Manager, HashiCorp Vault, etc.
```

### 2. Regular Updates

```bash
# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### 3. Monitoring & Alerts

Set up alerts in Grafana:
- High error rate (>5%)
- High response time (>2s p95)
- High memory usage (>80%)
- Disk space low (<10%)

### 4. Backup Strategy

```bash
# Automated daily backups
0 2 * * * /path/to/backup-script.sh

# Keep last 7 days of backups
# Test restore process monthly
```

---

## 📞 Support

### Documentation
- [Phase 5 Complete Guide](PHASE5_PRODUCTION_COMPLETE.md)
- [API Documentation](http://localhost/docs)
- [Architecture Overview](README.md)

### Community
- GitHub Issues: Report bugs and request features
- Discord: Join our community (coming soon)
- Email: support@example.com

### Professional Support
- Consulting: Custom implementation assistance
- Training: Team training sessions
- SLA Support: 24/7 support with SLA

---

## ✅ Deployment Checklist

Use this checklist for each deployment:

### Pre-Deployment
- [ ] Code reviewed and tested
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] SSL certificates valid
- [ ] Backup completed

### Deployment
- [ ] Pull latest code
- [ ] Build Docker images
- [ ] Run database migrations (if any)
- [ ] Deploy services
- [ ] Run health checks
- [ ] Verify all endpoints

### Post-Deployment
- [ ] Monitor logs for errors
- [ ] Check Grafana dashboards
- [ ] Test critical functionality
- [ ] Notify team of deployment
- [ ] Update deployment log

### Rollback Plan
- [ ] Previous Docker images tagged
- [ ] Rollback script tested
- [ ] Database backup available
- [ ] Team notified of rollback procedure

---

## 🎉 Success!

Your AI Financial Agent is now deployed and ready to process receipts with:

✅ **Production-grade security**  
✅ **Scalable infrastructure**  
✅ **Real-time monitoring**  
✅ **Automated deployments**  
✅ **High availability**

**Next Steps:**
1. Customize Grafana dashboards
2. Set up alerting rules
3. Configure backup automation
4. Plan for scaling
5. Monitor and optimize

---

*Last Updated: January 2025*  
*Version: 1.0.0*

