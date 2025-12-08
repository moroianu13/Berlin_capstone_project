# Monitoring & Logging Guide

## Quick Health Check

Run the monitoring script:
```bash
./.fly/scripts/monitor.sh
```

## View Real-Time Logs

```bash
# Stream live logs
flyctl logs -a berlin-rentwise

# Last 100 lines
flyctl logs -a berlin-rentwise --limit 100

# Filter by search term
flyctl logs -a berlin-rentwise | grep error
```

## Check App Status

```bash
# Overall status
flyctl status -a berlin-rentwise

# Machine details
flyctl machine list -a berlin-rentwise

# Check specific machine
flyctl machine status <machine-id>
```

## Monitor Database

```bash
# Database status
flyctl postgres db list -a berlin-rentwise-db

# Connect to database
flyctl postgres connect -a berlin-rentwise-db

# Database metrics
flyctl postgres db show -a berlin-rentwise-db
```

## Performance Monitoring

```bash
# View metrics
flyctl metrics -a berlin-rentwise

# Check machine resource usage
flyctl ssh console -a berlin-rentwise -C "top -b -n 1"
```

## Django Logs

Logs are stored in `/code/logs/django.log` inside the container:

```bash
# View Django logs
flyctl ssh console -a berlin-rentwise -C "tail -100 /code/logs/django.log"

# Follow Django logs in real-time
flyctl ssh console -a berlin-rentwise -C "tail -f /code/logs/django.log"
```

## Log Levels

- **DEBUG**: Detailed information (only in development)
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

## Common Monitoring Commands

### Check if app is responding
```bash
curl -I https://berlin-rentwise.fly.dev/
```

### Test chatbot endpoint
```bash
curl https://berlin-rentwise.fly.dev/neighborhoods/ | grep -i "berlin"
```

### Check static files
```bash
curl -I https://berlin-rentwise.fly.dev/static/css/general_and_home.css
```

### Monitor database connections
```bash
flyctl ssh console -a berlin-rentwise -C "python manage.py dbshell --command='SELECT count(*) FROM pg_stat_activity;'"
```

## Alerting (Manual)

Set up manual monitoring:

1. **Daily Health Check**: Run `./.fly/scripts/monitor.sh` daily
2. **Error Monitoring**: Check logs for ERROR/CRITICAL messages
3. **Performance**: Monitor response times with curl
4. **Database**: Check connection pool status

## Useful Fly.io Dashboard

Access the web dashboard at: https://fly.io/apps/berlin-rentwise

Features:
- Real-time metrics
- Log viewer
- Machine status
- Deployment history
- Billing information

## Debugging Issues

### App not responding
```bash
# Check machine state
flyctl status -a berlin-rentwise

# Restart machine
flyctl machine restart <machine-id>

# View recent errors
flyctl logs -a berlin-rentwise | grep -i error
```

### Database connection issues
```bash
# Check DATABASE_URL is set
flyctl ssh console -a berlin-rentwise -C "env | grep DATABASE"

# Test database connection
flyctl ssh console -a berlin-rentwise -C "python manage.py check --database default"
```

### High memory usage
```bash
# Check memory usage
flyctl ssh console -a berlin-rentwise -C "free -m"

# Scale up if needed
flyctl scale memory 1024 -a berlin-rentwise
```

## Log Rotation

Django logs automatically rotate when they reach 5MB, keeping the last 5 backups.

To view archived logs:
```bash
flyctl ssh console -a berlin-rentwise -C "ls -lh /code/logs/"
```

## Best Practices

1. ✅ Check logs daily for errors
2. ✅ Monitor response times weekly
3. ✅ Review database performance monthly
4. ✅ Keep an eye on Fly.io costs
5. ✅ Test AI chatbot functionality regularly
6. ✅ Monitor disk usage in database
7. ✅ Check for Django security updates
