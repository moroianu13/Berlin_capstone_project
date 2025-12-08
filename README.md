[![Django CI](https://github.com/moroianu13/Berlin_capstone_project/actions/workflows/django.yml/badge.svg)](https://github.com/moroianu13/Berlin_capstone_project/actions/workflows/django.yml)
[![Fly Deploy](https://github.com/moroianu13/Berlin_capstone_project/actions/workflows/fly-deploy.yml/badge.svg)](https://github.com/moroianu13/Berlin_capstone_project/actions/workflows/fly-deploy.yml)

# 🏙️ Berlin RentWise

**Live Demo:** [https://berlin-rentwise.fly.dev/](https://berlin-rentwise.fly.dev/)

A comprehensive Django web application for exploring Berlin neighborhoods, analyzing rental prices, crime data, and amenities. Features an AI-powered chatbot using Google Gemini for interactive assistance.

---

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Contributing](#contributing)

---

## ✨ Features

### Core Functionality
- **Neighborhood Explorer**: Browse 447 Berlin neighborhoods with detailed information
- **Borough Insights**: Explore 12 Berlin boroughs with geographic data
- **Rental Price Analysis**: View and filter neighborhoods by rental prices
- **Crime Data Visualization**: Access crime statistics for informed decision-making
- **Amenities Mapping**: Discover local amenities and facilities
- **Lifestyle Matching**: Find neighborhoods matching your lifestyle preferences

### AI Chatbot
- **Google Gemini Integration**: Natural language conversation powered by AI
- **Multi-tier Response System**:
  1. Dialog pattern matching (YAML-based)
  2. Predefined factual responses (fuzzy matching)
  3. Live weather API integration
  4. AI-generated responses (Google Gemini Flash)
  5. Wikipedia knowledge base
  6. Fallback fun facts
- **Conversation History**: Maintains session-based chat context
- **Berlin-specific Knowledge**: Specialized responses about Berlin neighborhoods

### Data & Analytics
- **Interactive Maps**: GeoJSON-based neighborhood boundaries
- **REST API**: Full CRUD operations for all data models
- **Advanced Filtering**: Search by price range, crime rate, amenities
- **Statistical Insights**: Rental trends and neighborhood comparisons

---

## 🛠️ Tech Stack

### Backend
- **Django 5.2.9** - Web framework
- **Django REST Framework 3.16.1** - API development
- **PostgreSQL 15** - Primary database
- **Gunicorn 23.0.0** - WSGI HTTP server

### AI & External APIs
- **Google Gemini API** (`google-generativeai==0.8.3`) - AI chatbot
- **OpenWeatherMap API** - Live weather data
- **Wikipedia API** - Knowledge base integration

### Data Processing
- **GeoPandas 1.1.1** - Geographic data manipulation
- **Pandas 2.3.3** - Data analysis
- **NumPy 2.2.6** - Numerical computing
- **PyProj 3.7.1** - Cartographic projections

### Frontend
- **Bootstrap 5** - UI framework
- **Leaflet.js** - Interactive maps
- **AJAX** - Asynchronous API calls
- **Jinja2 3.1.6** - Template engine

### DevOps & Deployment
- **Fly.io** - Production hosting (Frankfurt region)
- **Docker** - Containerization
- **WhiteNoise 6.8.2** - Static file serving
- **GitHub Actions** - CI/CD automation

### Testing & Quality
- **Django TestCase** - Unit & integration tests
- **unittest.mock** - Test mocking
- **PostgreSQL Test Database** - Isolated test environment

### Development Tools
- **python-dotenv 1.2.1** - Environment variable management
- **drf-yasg 1.21.11** - API documentation (Swagger/OpenAPI)
- **BeautifulSoup4 4.14.3** - HTML parsing
- **FuzzyWuzzy 0.18.0** - Fuzzy string matching

---

## 🏗️ Architecture

### System Design
```
┌─────────────────┐
│   GitHub Repo   │
└────────┬────────┘
         │ (push to main)
         ▼
┌─────────────────┐
│   GitHub Actions│
│   - Django CI   │ ──► Run Tests (PostgreSQL)
│   - Fly Deploy  │ ──► Deploy to Production
└────────┬────────┘
         │ (if tests pass)
         ▼
┌─────────────────┐
│    Fly.io       │
│  - Gunicorn     │
│  - PostgreSQL   │
│  - Auto-scaling │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  External APIs  │
│  - Gemini AI    │
│  - Weather API  │
│  - Wikipedia    │
└─────────────────┘
```

### Application Flow
1. **User Request** → Nginx (if local) / Fly.io proxy → Gunicorn
2. **Django Views** → Process request → Query PostgreSQL
3. **Chatbot Request** → Dialog matching → Predefined responses → AI API
4. **API Calls** → DRF ViewSets → Serializers → JSON response
5. **Static Files** → WhiteNoise → Cached & compressed

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Git
- Virtual environment tool (venv/conda)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/moroianu13/Berlin_capstone_project.git
   cd Berlin_capstone_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env_docker .env
   # Edit .env with your credentials:
   # - SECRET_KEY
   # - DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
   # - GEMINI_API_KEY
   # - WEATHER_API_KEY
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Load initial data**
   ```bash
   python manage.py loaddata data.json
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

   Access the app at `http://localhost:8000`

### Docker Setup

```bash
docker-compose up -d --build
```

Access the app at `http://localhost:80`

---

## 🌐 Deployment

### Fly.io Production Deployment

The application is deployed to Fly.io with automatic CI/CD.

**Manual Deployment:**
```bash
# Login to Fly.io
flyctl auth login

# Deploy
flyctl deploy

# Check status
flyctl status -a berlin-rentwise

# View logs
flyctl logs -a berlin-rentwise
```

**Configuration:**
- **Region**: Frankfurt (fra) - closest to Berlin
- **Resources**: 512MB RAM, 1 shared CPU
- **Database**: Fly PostgreSQL with pgbouncer
- **Scaling**: Auto-stop/start enabled for cost optimization
- **Health Checks**: Automatic HTTP health monitoring

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment guide.

---

## 🔄 CI/CD Pipeline

### Automated Workflow

1. **Push to main** → Triggers GitHub Actions
2. **Django CI** (`.github/workflows/django.yml`)
   - Set up Python 3.10
   - Install dependencies
   - Create test database (PostgreSQL 14)
   - Run 44 unit/integration tests
   - ✅ Pass → Trigger deployment
   - ❌ Fail → Block deployment

3. **Fly Deploy** (`.github/workflows/fly-deploy.yml`)
   - Only runs if CI passes
   - Checkout code
   - Deploy to Fly.io
   - Run migrations
   - Restart application

### Secrets Configuration
Required GitHub repository secrets:
- `FLY_API_TOKEN` - Fly.io authentication token

---

## 📚 API Documentation

### REST Endpoints

**Neighborhoods**
```
GET    /api/neighborhoods/          # List all neighborhoods
POST   /api/neighborhoods/          # Create neighborhood
GET    /api/neighborhoods/{id}/     # Retrieve neighborhood
PUT    /api/neighborhoods/{id}/     # Update neighborhood
DELETE /api/neighborhoods/{id}/     # Delete neighborhood
```

**Boroughs**
```
GET    /api/boroughs/               # List all boroughs
POST   /api/boroughs/               # Create borough
GET    /api/boroughs/{id}/          # Retrieve borough
PUT    /api/boroughs/{id}/          # Update borough
DELETE /api/boroughs/{id}/          # Delete borough
```

**Crime Data**
```
GET    /api/crime/                  # List crime statistics
```

**Amenities**
```
GET    /api/amenities/              # List amenities
```

**Chat**
```
POST   /chat/                       # Send chat message
Body: {"message": "Your question here"}
Response: {"response": "AI/bot response"}
```

### Swagger Documentation
Access interactive API docs at: `/swagger/`

---

## 📁 Project Structure

```
Berlin_capstone_project/
├── .github/
│   └── workflows/
│       ├── django.yml          # CI testing workflow
│       ├── fly-deploy.yml      # CD deployment workflow
│       └── django_cd.yml       # EC2 deployment (disabled)
├── .fly/
│   └── scripts/
│       └── monitor.sh          # Health check script
├── data/
│   ├── dialog.yaml             # Chatbot dialog patterns
│   ├── factual_responses.yaml # Predefined Q&A
│   └── data.json               # Initial database fixtures
├── docs/                       # Documentation
├── logs/                       # Application logs
├── neighborhoods/              # Main Django app
│   ├── models.py               # Data models
│   ├── views.py                # View logic & chatbot
│   ├── serializers.py          # DRF serializers
│   ├── urls.py                 # URL routing
│   ├── templates/              # HTML templates
│   └── tests/                  # Test suite
├── rentfinder/                 # Django project settings
│   ├── settings.py             # Configuration
│   ├── urls.py                 # Root URL config
│   └── wsgi.py                 # WSGI application
├── static/                     # Static files (CSS, JS, images)
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Local development stack
├── fly.toml                    # Fly.io configuration
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── DEPLOYMENT.md               # Deployment guide
├── MONITORING.md               # Monitoring guide
└── README.md                   # This file
```

---

## 🔐 Environment Variables

### Required Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,.fly.dev
CSRF_TRUSTED_ORIGINS=https://berlin-rentwise.fly.dev

# Database
DB_NAME=berlin_capstone
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# External APIs
GEMINI_API_KEY=your-gemini-api-key
WEATHER_API_KEY=your-openweathermap-key
```

### Development vs Production
- **Development**: Use `.env` file with DEBUG=True
- **Production**: Use Fly.io secrets with DEBUG=False

```bash
# Set Fly.io secrets
flyctl secrets set SECRET_KEY=xxx
flyctl secrets set GEMINI_API_KEY=xxx
flyctl secrets set WEATHER_API_KEY=xxx
```

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test Module
```bash
python manage.py test neighborhoods.tests.test_view
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Structure
- **44 total tests** covering:
  - Model operations (CRUD)
  - API endpoints (ViewSets)
  - Chat functionality
  - Authentication & permissions
  - Data validation
  - Edge cases & error handling

---

## 📊 Monitoring

### Production Monitoring

**Check Application Status:**
```bash
flyctl status -a berlin-rentwise
```

**View Real-time Logs:**
```bash
flyctl logs -a berlin-rentwise
```

**Access Django Logs:**
```bash
flyctl ssh console -a berlin-rentwise
cat /code/logs/django.log
```

**Database Monitoring:**
```bash
flyctl postgres connect -a berlin-rentwise-db
```

See [MONITORING.md](./MONITORING.md) for comprehensive monitoring guide.

### Logging Configuration
- **Log Rotation**: 5MB files, 5 backups
- **Log Levels**: DEBUG (dev), INFO (prod)
- **Log Location**: `/code/logs/django.log`

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Write tests for new features
- Follow PEP 8 style guide
- Update documentation
- Ensure CI tests pass

---

## 📄 License

This project is part of an academic capstone project.

---

## 👨‍💻 Author

**Adrian Moroianu**
- GitHub: [@moroianu13](https://github.com/moroianu13)
- Project: Berlin RentWise - Data Science Capstone

---

## 🙏 Acknowledgments

- **Berlin Open Data** - Neighborhood and geographic data
- **Google Gemini** - AI chatbot capabilities
- **OpenWeatherMap** - Weather API
- **Fly.io** - Production hosting platform
- **Django Community** - Framework and ecosystem

---

## 📈 Project Timeline

1. **Data Collection & Cleaning** - Gathered Berlin neighborhood data
2. **Database Design** - Structured PostgreSQL schema
3. **API Development** - Built REST endpoints with DRF
4. **Frontend Development** - Created interactive UI
5. **AI Integration** - Implemented Gemini chatbot
6. **Testing & QA** - Comprehensive test suite
7. **Deployment** - Fly.io production setup
8. **CI/CD Pipeline** - Automated testing & deployment
9. **Monitoring & Optimization** - Performance tuning

---

**Built with ❤️ in Berlin**
