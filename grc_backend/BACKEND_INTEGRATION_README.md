# GRC + TPRM Backend Integration Guide

This guide explains how the GRC and TPRM backends have been integrated to work as a single Django application.

## Overview

The integration combines both GRC (Governance, Risk, and Compliance) and TPRM (Third-Party Risk Management) backends into a single Django project while maintaining their separate databases.

### Architecture

```
grc_backend/
├── backend/                    # Main Django project
│   ├── settings.py            # Combined settings (GRC + TPRM)
│   ├── urls.py                # Combined URL routing
│   └── tprm_db_router.py      # Database router for TPRM
├── grc/                       # GRC app (uses 'default' database)
└── tprm_backend/              # TPRM apps (uses 'tprm' database)
    ├── rfp/
    ├── contracts/
    ├── slas/
    ├── bcpdrp/
    └── ... (other TPRM apps)
```

## URL Structure

- **GRC Routes**: `/api/...` (existing GRC routes)
- **TPRM Routes**: `/api/tprm/...` (all TPRM routes prefixed with `/tprm/`)

### TPRM API Endpoints

| Module | URL Prefix |
|--------|------------|
| Authentication (MFA) | `/api/tprm/auth/` |
| RBAC | `/api/tprm/rbac/` |
| Admin Access | `/api/tprm/admin-access/` |
| Global Search | `/api/tprm/global-search/` |
| Core | `/api/tprm/core/` |
| OCR | `/api/tprm/ocr/` |
| SLA Management | `/api/tprm/slas/` |
| Audits | `/api/tprm/audits/` |
| Notifications | `/api/tprm/notifications/` |
| Quick Access | `/api/tprm/quick-access/` |
| Compliance | `/api/tprm/compliance/` |
| BCP/DRP | `/api/tprm/bcpdrp/` |
| Risk Analysis | `/api/tprm/risk-analysis/` |
| Contracts | `/api/tprm/contracts/` |
| Contract Audits | `/api/tprm/audits-contract/` |
| Contract Risk Analysis | `/api/tprm/contract-risk-analysis/` |
| RFP Management | `/api/tprm/rfp/` |
| RFP Approval | `/api/tprm/rfp-approval/` |
| RFP Risk Analysis | `/api/tprm/rfp-risk-analysis/` |
| Vendor Core | `/api/tprm/vendor-core/` |
| Vendor Auth | `/api/tprm/vendor-auth/` |
| Vendor Risk | `/api/tprm/vendor-risk/` |
| Vendor Questionnaire | `/api/tprm/vendor-questionnaire/` |
| Vendor Dashboard | `/api/tprm/vendor-dashboard/` |
| Vendor Lifecycle | `/api/tprm/vendor-lifecycle/` |
| Vendor Approval | `/api/tprm/vendor-approval/` |
| Vendor Risk Analysis | `/api/tprm/risk-analysis-vendor/` |

## Database Configuration

The system uses two separate databases:

### GRC Database (default)
```python
DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": os.environ.get("DB_NAME", "grc2"),
        "USER": os.environ.get("DB_USER", "admin"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "password"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "3306"),
    }
}
```

### TPRM Database
```python
DATABASES = {
    "tprm": {
        "ENGINE": 'django.db.backends.mysql',
        "NAME": os.environ.get("TPRM_DB_NAME", "tprm_integration"),
        "USER": os.environ.get("TPRM_DB_USER", "admin"),
        "PASSWORD": os.environ.get("TPRM_DB_PASSWORD", "password"),
        "HOST": os.environ.get("TPRM_DB_HOST", "localhost"),
        "PORT": os.environ.get("TPRM_DB_PORT", "3306"),
    }
}
```

## Environment Variables

Create a `.env` file in the `grc_backend` directory with the following variables:

```env
# GRC Database
DB_NAME=grc2
DB_USER=admin
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# TPRM Database
TPRM_DB_NAME=tprm_integration
TPRM_DB_USER=admin
TPRM_DB_PASSWORD=your_password
TPRM_DB_HOST=tprmintegration.c1womgmu83di.ap-south-1.rds.amazonaws.com
TPRM_DB_PORT=3306

# Django Secret Key
DJANGO_SECRET_KEY=your-secret-key-here
```

## Installation

1. **Install dependencies:**
   ```bash
   cd grc_backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Copy the `.env.example` to `.env`
   - Update the database credentials

3. **Run the server:**
   ```bash
   python manage.py runserver
   ```

## Running the Combined Backend

### Development
```bash
cd grc_backend
python manage.py runserver 0.0.0.0:8000
```

### Production
```bash
gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

## Authentication

Both GRC and TPRM share the same authentication mechanism. Users authenticated through GRC's JWT/session authentication can access both GRC and TPRM endpoints.

### GRC Authentication Endpoints
- Login: `POST /api/jwt/login/`
- Refresh: `POST /api/jwt/refresh/`
- Logout: `POST /api/jwt/logout/`
- Verify: `POST /api/jwt/verify/`

### TPRM MFA Authentication (Optional)
- Login Step 1: `POST /api/tprm/auth/login/`
- Verify OTP: `POST /api/tprm/auth/verify-otp/`
- Resend OTP: `POST /api/tprm/auth/resend-otp/`

## Frontend Integration

Update your frontend to use the correct API base URLs:

```javascript
// GRC API calls
const grcApi = axios.create({
  baseURL: 'http://localhost:8000/api/'
});

// TPRM API calls
const tprmApi = axios.create({
  baseURL: 'http://localhost:8000/api/tprm/'
});
```

## Troubleshooting

### Database Connection Issues
- Ensure both databases are accessible from your server
- Check firewall rules for database ports
- Verify credentials in `.env` file

### Import Errors
- If you see import errors for TPRM modules, ensure `tprm_backend/__init__.py` exists
- Run `pip install -r requirements.txt` to install all dependencies

### Migration Issues
- TPRM uses existing database tables and doesn't require Django migrations
- GRC migrations should run on the `default` database only

## Notes

1. **Database Isolation**: The database router ensures TPRM models always use the 'tprm' database, preventing accidental data mixing.

2. **App Labels**: TPRM apps have unique labels (prefixed with `tprm_`) to avoid conflicts with any similarly-named GRC apps.

3. **Backward Compatibility**: The integration maintains backward compatibility with existing API endpoints.


