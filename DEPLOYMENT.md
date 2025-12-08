Y# Deployment Guide - Berlin RentWise on Fly.io

## Prerequisites
- Fly.io CLI installed: `curl -L https://fly.io/install.sh | sh`
- Fly.io account: Sign up at https://fly.io/

## Step 1: Login to Fly.io
```bash
flyctl auth login
```

## Step 2: Create PostgreSQL Database
```bash
flyctl postgres create --name berlin-rentwise-db --region fra --initial-cluster-size 1 --vm-size shared-cpu-1x --volume-size 1
```

## Step 3: Create the App (Don't Deploy Yet)
```bash
flyctl launch --no-deploy
# Choose app name: berlin-rentwise
# Choose region: fra (Frankfurt)
# Don't setup PostgreSQL (we already did)
```

## Step 4: Attach Database to App
```bash
flyctl postgres attach berlin-rentwise-db --app berlin-rentwise
```

## Step 5: Set Environment Variables
```bash
# Django secret key (generate a new one for production!)
flyctl secrets set SECRET_KEY="your-super-secret-production-key-here" --app berlin-rentwise

# Debug mode (False for production)
flyctl secrets set DEBUG="False" --app berlin-rentwise

# Allowed hosts
flyctl secrets set ALLOWED_HOSTS="berlin-rentwise.fly.dev,.fly.dev" --app berlin-rentwise

# CSRF trusted origins
flyctl secrets set CSRF_TRUSTED_ORIGINS="https://berlin-rentwise.fly.dev" --app berlin-rentwise

# Weather API key
flyctl secrets set WEATHER_API_KEY="your-weather-api-key" --app berlin-rentwise

# Gemini API key
flyctl secrets set GEMINI_API_KEY="your-gemini-api-key" --app berlin-rentwise
```

## Step 6: Deploy the App
```bash
flyctl deploy
```

## Step 7: Run Database Migrations
```bash
flyctl ssh console --app berlin-rentwise
# Inside the container:
python manage.py migrate
python manage.py collectstatic --noinput
exit
```

## Step 8: Load Initial Data
```bash
flyctl ssh console --app berlin-rentwise
# Inside the container:
python manage.py loaddata data.json
exit
```

## Step 9: Create Superuser (Optional)
```bash
flyctl ssh console --app berlin-rentwise
python manage.py createsuperuser
exit
```

## Access Your App
- **Website**: https://berlin-rentwise.fly.dev
- **Admin Panel**: https://berlin-rentwise.fly.dev/admin
- **API Docs**: https://berlin-rentwise.fly.dev/swagger

## Useful Commands

### View Logs
```bash
flyctl logs --app berlin-rentwise
```

### Check App Status
```bash
flyctl status --app berlin-rentwise
```

### Scale App
```bash
flyctl scale count 1 --app berlin-rentwise
```

### SSH into Container
```bash
flyctl ssh console --app berlin-rentwise
```

### Check Database Connection
```bash
flyctl postgres connect --app berlin-rentwise-db
```

### Update Environment Variables
```bash
flyctl secrets set VARIABLE_NAME="value" --app berlin-rentwise
```

### Redeploy After Code Changes
```bash
git add .
git commit -m "your changes"
git push
flyctl deploy
```

## Troubleshooting

### Static Files Not Loading
```bash
flyctl ssh console --app berlin-rentwise
python manage.py collectstatic --noinput --clear
exit
```

### Database Connection Issues
Check DATABASE_URL is set:
```bash
flyctl secrets list --app berlin-rentwise
```

### View App Secrets
```bash
flyctl secrets list --app berlin-rentwise
```

### Restart App
```bash
flyctl apps restart berlin-rentwise
```

## Cost Optimization
- Free tier includes: 3 shared VMs, 3GB storage
- App auto-stops when idle (auto_stop_machines = "stop")
- Auto-starts on request (auto_start_machines = true)
- Minimum 0 machines running (min_machines_running = 0)

## Security Checklist
- ✅ SECRET_KEY is different from development
- ✅ DEBUG = False in production
- ✅ ALLOWED_HOSTS configured
- ✅ CSRF_TRUSTED_ORIGINS configured
- ✅ API keys stored as secrets
- ✅ Database credentials auto-managed by Fly.io

## Next Steps After Deployment
1. Test all features on production URL
2. Set up custom domain (optional)
3. Enable monitoring and alerts
4. Configure backups for PostgreSQL
