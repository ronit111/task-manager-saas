# Operations Runbook - Task Manager SaaS

## Quick Reference

| What | Command |
|------|---------|
| SSH to server | `ssh -i ~/.ssh/task-manager-key.pem ubuntu@51.20.16.125` |
| Check app status | `docker ps` |
| View logs | `docker-compose logs -f` |
| Restart app | `docker-compose restart` |
| Deploy latest | `./deploy.sh` |

---

## 1. Connecting to the Server

```bash
ssh -i ~/.ssh/task-manager-key.pem ubuntu@51.20.16.125
```

If connection times out:
1. Check EC2 instance is running in AWS Console
2. Verify your IP is in the security group (EC2 → Security Groups → task-manager-sg)

---

## 2. Checking Application Status

### Is the container running?
```bash
docker ps
```
Expected: Container `task-manager-saas_web_1` with status "Up"

### Health check
```bash
curl http://localhost:5001/health
```
Expected: `{"service": "task-manager", "status": "healthy"}`

### Check from outside
```bash
curl http://51.20.16.125/health
```

---

## 3. Viewing Logs

### Application logs (live)
```bash
cd ~/task-manager-saas
docker-compose logs -f
```
Press `Ctrl+C` to stop

### Last 100 lines
```bash
docker-compose logs --tail 100
```

### Nginx logs
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 4. Restarting the Application

### Soft restart (keeps data)
```bash
cd ~/task-manager-saas
docker-compose restart
```

### Full restart (rebuilds container)
```bash
cd ~/task-manager-saas
docker-compose down
docker-compose up -d
```

### Restart Nginx
```bash
sudo systemctl restart nginx
```

---

## 5. Deploying Updates

### Automatic (via CI/CD)
Push to `main` branch → GitHub Actions deploys automatically

### Manual deployment
```bash
cd ~/task-manager-saas
./deploy.sh
```

The deploy script:
1. Pulls latest code from GitHub
2. Rebuilds Docker image
3. Restarts container

---

## 6. Rollback to Previous Version

```bash
cd ~/task-manager-saas

# See recent commits
git log --oneline -10

# Rollback to specific commit
git checkout <commit-hash>

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

To return to latest:
```bash
git checkout main
git pull origin main
docker-compose down && docker-compose build && docker-compose up -d
```

---

## 7. Common Issues & Fixes

### App not responding

1. Check container is running: `docker ps`
2. If not running: `docker-compose up -d`
3. Check logs for errors: `docker-compose logs --tail 50`

### 502 Bad Gateway

Nginx can't reach the app:
1. Check container: `docker ps`
2. Check port mapping: Should show `5001->5000`
3. Restart: `docker-compose restart`

### Disk space full

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a

# Clean old logs
sudo journalctl --vacuum-time=7d
```

### High CPU/Memory

```bash
# Check resources
htop

# Restart container (frees memory)
docker-compose restart
```

### Database issues

SQLite database is at: `~/task-manager-saas/instance/tasks.db`

```bash
# Backup database
cp instance/tasks.db instance/tasks.db.backup

# Check database exists
ls -la instance/
```

---

## 8. Monitoring Commands

### Server resources
```bash
# CPU and memory
htop

# Disk space
df -h

# Network connections
netstat -tlnp
```

### Docker stats
```bash
docker stats
```

---

## 9. Security Checklist

- [ ] SSH key has correct permissions (`chmod 400`)
- [ ] Security group limits SSH to known IPs (or GitHub Actions)
- [ ] No secrets in code (use environment variables)
- [ ] Regular OS updates: `sudo apt update && sudo apt upgrade`

---

## 10. Contact & Escalation

**Instance Details:**
- IP: 51.20.16.125
- Region: eu-north-1 (Stockholm)
- Instance Type: t2.micro
- OS: Ubuntu 22.04

**GitHub Repo:** https://github.com/ronit111/task-manager-saas

**AWS Console:** https://console.aws.amazon.com/ec2/
