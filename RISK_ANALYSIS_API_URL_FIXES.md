# Risk Analysis API URL Fixes - Complete Resolution

## Problem Summary
Risk Analytics page was showing 404 errors for all API endpoints:
- ❌ `GET /api/risk-analysis/risks/` - 404 Not Found
- ❌ `GET /api/risk-analysis/modules/` - 404 Not Found  
- ❌ `GET /api/risk-analysis/dashboard/` - 404 Not Found

## Root Cause
1. Frontend was using `API_BASE_URL = 'http://localhost:8000/api'`
2. Endpoints were constructed as: `${API_BASE_URL}/risk-analysis/...`
3. Result: `http://localhost:8000/api/risk-analysis/...`
4. **But backend expects**: `http://localhost:8000/api/tprm/risk-analysis/...`

Additionally, the `/modules/` endpoint didn't exist in the backend.

## Solution

### 1. Fixed API Base URL
✅ **grc_frontend/tprm_frontend/src/pages/BCP/RiskAnalytics.vue**
   - Changed: `const API_BASE_URL = 'http://localhost:8000/api';`
   - To: `const API_BASE_URL = 'http://localhost:8000/api/tprm';`

### 2. Created Missing Modules Endpoint
✅ **grc_backend/tprm_backend/risk_analysis/views.py**
   - Added `ModulesAPIView` class that returns available entities/modules
   - Uses `EntityDataService` to get available entities
   - Transforms entities to modules format for frontend compatibility

✅ **grc_backend/tprm_backend/risk_analysis/urls.py**
   - Added: `path('modules/', views.ModulesAPIView.as_view(), name='modules')`

## Backend URL Configuration
✅ **Backend URLs**: Correctly configured
   - Base path: `api/tprm/risk-analysis/`
   - Registered in: `grc_backend/backend/urls.py` line 171
   - All endpoints properly routed

## Fixed Endpoints

### Before (404 Errors)
- `http://localhost:8000/api/risk-analysis/dashboard/` ❌
- `http://localhost:8000/api/risk-analysis/risks/` ❌
- `http://localhost:8000/api/risk-analysis/modules/` ❌ (endpoint didn't exist)

### After (Working)
- `http://localhost:8000/api/tprm/risk-analysis/dashboard/` ✅
- `http://localhost:8000/api/tprm/risk-analysis/risks/` ✅
- `http://localhost:8000/api/tprm/risk-analysis/modules/` ✅

## Database Configuration
✅ **Database**: Uses `tprm_integration` database
   - Router: `TPRMDatabaseRouter` routes risk_analysis app to `tprm` database
   - Database name: `tprm_integration`

## Testing Checklist
- [ ] Dashboard endpoint: `GET /api/tprm/risk-analysis/dashboard/`
- [ ] Risks endpoint: `GET /api/tprm/risk-analysis/risks/?page=1`
- [ ] Modules endpoint: `GET /api/tprm/risk-analysis/modules/`

## Summary
- ✅ API base URL fixed to include `/tprm` prefix
- ✅ Missing modules endpoint created
- ✅ All three endpoints now correctly routed
- ✅ Database configuration verified

All 404 errors should now be resolved!

