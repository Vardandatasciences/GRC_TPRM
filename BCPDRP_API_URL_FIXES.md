# BCPDRP API URL Fixes - Complete Resolution

## Problem Summary
All BCPDRP pages were showing 404 errors because API URLs had duplicate `/api/` in the path:
- ❌ **Wrong**: `http://localhost:8000/api/tprm/api/bcpdrp/...`
- ✅ **Correct**: `http://localhost:8000/api/tprm/bcpdrp/...`

## Root Cause
1. Axios instance (`http`) has baseURL: `http://localhost:8000/api/tprm`
2. Endpoints were using: `/api/bcpdrp/...`
3. Result: BaseURL + Endpoint = `http://localhost:8000/api/tprm/api/bcpdrp/...` (duplicate `/api/`)

## Solution
Changed all endpoints from `/api/bcpdrp/...` to `/bcpdrp/...` so they combine correctly with the base URL.

## Files Fixed

### 1. Core API Service
✅ **grc_frontend/tprm_frontend/src/services/api_bcp.js**
   - Fixed all 30+ endpoint definitions
   - Changed `/api/bcpdrp/*` → `/bcpdrp/*`

### 2. Vue Components
✅ **grc_frontend/tprm_frontend/src/pages/BCP/PlanLibrary.vue**
   - Fixed strategies endpoint
   - Fixed plans endpoint
   - Fixed comprehensive plan detail endpoint

✅ **grc_frontend/tprm_frontend/src/pages/BCP/OcrExtraction.vue**
   - Fixed OCR plans list endpoint
   - Fixed OCR plan detail endpoint
   - Fixed OCR status update endpoints (3 occurrences)
   - Fixed OCR extract endpoint

✅ **grc_frontend/tprm_frontend/src/pages/BCP/QuestionnaireLibrary.vue**
   - Fixed plans fetch endpoint
   - Fixed users fetch endpoint
   - Fixed questionnaire assign endpoint

✅ **grc_frontend/tprm_frontend/src/pages/BCP/QuestionnaireBuilder.vue**
   - Fixed questionnaire review endpoint

✅ **grc_frontend/tprm_frontend/src/pages/BCP/QuestionnaireAssignmentWorkflow.vue**
   - Fixed plans fetch endpoint
   - Fixed questionnaire assign endpoint

✅ **grc_frontend/tprm_frontend/src/pages/BCP/PlanSubmissionOcr.vue**
   - Fixed OCR status update endpoint

### 3. API Utilities
✅ **grc_frontend/tprm_frontend/src/api/questionnaire.js**
   - Fixed all questionnaire endpoints (get, create, update, delete)
   - Fixed questionnaire detail endpoint

✅ **grc_frontend/tprm_frontend/src/pages/QuestionnaireTemplates.vue**
   - Fixed questionnaire template save endpoint (uses apiClient with different baseURL, so needs full path)

## Database Configuration Verification
✅ **Database Router**: Correctly configured
   - Router: `backend.tprm_router.TPRMDatabaseRouter`
   - Routes BCPDRP app to: `tprm` database (database name: `tprm_integration`)
   - App label `bcpdrp` is in the `tprm_apps` set

✅ **Database Settings**: 
   - Database key: `tprm`
   - Database name: `tprm_integration`
   - Host: `tprmintegration.c1womgmu83di.ap-south-1.rds.amazonaws.com`

## Backend URL Configuration
✅ **Backend URLs**: Correctly configured
   - Base path: `api/tprm/bcpdrp/`
   - Registered in: `grc_backend/backend/urls.py` line 168
   - All endpoints properly routed

## Console Log Statements
ℹ️ **Note**: Several console.log statements still contain `/api/bcpdrp/...` paths, but these are informational only and don't affect functionality. They can be updated later for consistency.

Files with console.log statements:
- PlanSubmissionOcr.vue
- QuestionnaireAssignmentWorkflow.vue
- QuestionnaireBuilder.vue
- QuestionnaireWorkflow.vue
- QuestionnaireAssignment.vue
- MyApprovals.vue
- ApprovalAssignment.vue

## Testing Checklist
- [ ] Plans list endpoint: `/api/tprm/bcpdrp/plans/`
- [ ] Users list endpoint: `/api/tprm/bcpdrp/users/`
- [ ] Strategies list endpoint: `/api/tprm/bcpdrp/strategies/`
- [ ] Dropdowns endpoint: `/api/tprm/bcpdrp/dropdowns/`
- [ ] OCR plans endpoint: `/api/tprm/bcpdrp/ocr/plans/`
- [ ] Questionnaires endpoint: `/api/tprm/bcpdrp/questionnaires/`
- [ ] Approvals endpoint: `/api/tprm/bcpdrp/approvals/`
- [ ] Dashboard endpoint: `/api/tprm/bcpdrp/dashboard/overview/`

## Summary
- ✅ All API URLs fixed
- ✅ Database configuration verified (uses `tprm_integration`)
- ✅ Backend URL routing verified
- ✅ All Vue components updated
- ✅ All API service files updated

All 404 errors should now be resolved!

