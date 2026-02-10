# Security Guidelines

## ⚠️ IMPORTANT: Exposed API Keys

### Immediate Actions Required

**Your API keys have been exposed in the local environment. You must:**

1. **Revoke and regenerate ALL API keys immediately:**
   - Google Gemini API Key: https://makersuite.google.com/app/apikey
   - Weather API Key: https://www.weatherapi.com/

2. **Update your secrets:**
   - Copy `.env_docker.example` to `.env_docker`
   - Fill in the NEW API keys
   - Never commit `.env_docker` to git (it's already in .gitignore)

### Setting Up Secrets Properly

#### Local Development
```bash
# 1. Copy the example file
cp .env_docker.example .env_docker

# 2. Edit with your actual keys
nano .env_docker
```

#### GitHub Secrets (for CI/CD)
Go to: Repository Settings → Secrets and Variables → Actions

Add these secrets:
- `SECRET_KEY`
- `GEMINI_API_KEY`
- `WEATHER_API_KEY`

#### Fly.io Secrets (if you use it again)
```bash
flyctl secrets set GEMINI_API_KEY="your-new-key"
flyctl secrets set SECRET_KEY="your-django-secret"
```

### Generate a New Django Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Security Best Practices

### ✅ DO:
- Use environment variables for all secrets
- Keep `.env*` files in `.gitignore`
- Use different keys for development and production
- Rotate API keys regularly
- Use strong, randomly generated passwords
- Enable 2FA on all API provider accounts

### ❌ DON'T:
- Commit API keys to git
- Share API keys in chat/email
- Use the same keys across environments
- Use default/example passwords in production
- Hardcode secrets in source code

## Current Security Status

### ✅ Secure:
- `.env*` files are in `.gitignore`
- Settings.py uses environment variables
- Default SECRET_KEY has warning comment
- Database credentials use environment variables

### ⚠️ Needs Attention:
- **REVOKE exposed API keys immediately**
- Generate new production SECRET_KEY
- Update all secrets with new values

## Checking for Exposed Secrets

Run this to check for accidentally committed secrets:
```bash
git log --all --full-history -- .env* .env_docker .env_local
```

If you find any, contact GitHub Support to remove sensitive data from history.
