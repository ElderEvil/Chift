# VPS Deployment Guide

Deploy Chift to your VPS using Docker Compose.

## Prerequisites

- ✅ Ubuntu 20.04+ VPS with Docker and Docker Compose installed
- ✅ A working Odoo instance with credentials
- ✅ Domain name (optional, for SSL)

## Quick Setup

### 1. Install Docker & Docker Compose

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose-plugin -y

# Reboot to apply group changes
sudo reboot
```

### 2. Deploy Application

```bash
# Clone repository
git clone git@github.com:ElderEvil/Chift.git
cd chift

# Create environment file
cp .env.example .env
nano .env  # Edit with your credentials

# Start services
docker-compose up -d

# Run database migrations
docker-compose exec app alembic upgrade head

# Create admin user
docker-compose exec app python -m scripts.create_admin
```

### 3. Configure Reverse Proxy (Optional)

**Nginx Configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Install Nginx:**
```bash
sudo apt install nginx -y
sudo cp nginx-config /etc/nginx/sites-available/chift
sudo ln -s /etc/nginx/sites-available/chift /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 4. SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Environment Variables

Create `.env` file with:

```env
# Odoo Configuration
ODOO_URL=https://your-odoo.com
ODOO_DB=your-database
ODOO_USERNAME=your-username
ODOO_PASSWORD=your-password

# Security
SECRET_KEY=your-32-char-secret-key

# Optional
SYNC_INTERVAL_MINUTES=15
```

## Management Commands

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d

# Backup database
docker-compose exec db pg_dump -U chift chift_db > backup.sql
```

## Health Check

```bash
curl http://localhost:8000/health
```

## Troubleshooting

- **Database connection**: Check `DATABASE_URL` in docker-compose.yml
- **Odoo connection**: Verify Odoo credentials and network access
- **Port conflicts**: Ensure ports 5432 and 8000 are available
- **Permissions**: Ensure user is in docker group

## Security

- ✅ Use strong `SECRET_KEY`
- ✅ Change default database credentials
- ✅ Enable firewall (ufw)
- ✅ Use SSL certificates in production
- ✅ Regularly update Docker images
