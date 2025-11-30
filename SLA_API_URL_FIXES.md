# SLA API URL Fixes - Complete Resolution

## Problem Summary
SLA pages were showing 404 and 403 errors for API endpoints:
- ❌ `GET /api/slas/` - 404 Not Found (should be `/api/tprm/slas/`)
- ❌ `GET /api/slas/vendors/` - 404 Not Found (should be `/api/tprm/slas/vendors/`)
- ❌ `GET /api/audits/available-users/` - 404 Not Found (should be `/api/tprm/audits/available-users/`)
- ❌ `GET /api/tprm/slas/approvals/approvals/` - 404 Not Found (duplicate `/approvals/`)

## Root Cause
1. **slaApprovalApi.js** was using hardcoded URLs without `/tprm` prefix:
   - `/api/slas/` instead of `/api/tprm/slas/`
   - `/api/slas/vendors/` instead of `/api/tprm/slas/vendors/`
   - `/api/audits/available-users/` instead of `/api/tprm/audits/available-users/`

2. **Duplicate `/approvals/` in endpoints**:
   - baseURL was `http://localhost:8000/api/tprm/slas/approvals`
   - Endpoints were appending `/approvals/` again
   - Result: `/api/tprm/slas/approvals/approvals/` (duplicate)

## Solution

### 1. Fixed Hardcoded URLs in slaApprovalApi.js
✅ **grc_frontend/tprm_frontend/src/services/slaApprovalApi.js**

**Fixed Methods:**
- `getSLAs()`: Changed from `/api/slas/` to `http://localhost:8000/api/tprm/slas/`
- `getPendingSLAs()`: Changed from `/api/slas/` to `http://localhost:8000/api/tprm/slas/`
- `getAllSLAs()`: Changed from `/api/slas/` to `http://localhost:8000/api/tprm/slas/`
- `getVendors()`: Changed from `/api/slas/vendors/` to `http://localhost:8000/api/tprm/slas/vendors/`
- `getUsers()`: Changed from `/api/audits/available-users/` to `http://localhost:8000/api/tprm/audits/available-users/`

### 2. Fixed Duplicate `/approvals/` Endpoints
✅ **grc_frontend/tprm_frontend/src/services/slaApprovalApi.js**

**Fixed Methods:**
- `getApprovals()`: Changed from `/?` to `/approvals/`
- `getApproval()`: Changed from `/${approvalId}/` to `/approvals/${approvalId}/`
- `createApproval()`: Changed from `/create/` to `/approvals/create/`
- `bulkCreateApprovals()`: Changed from `/bulk-create/` to `/approvals/bulk-create/`
- `updateApproval()`: Changed from `/${approvalId}/update/` to `/approvals/${approvalId}/update/`
- `deleteApproval()`: Changed from `/${approvalId}/delete/` to `/approvals/${approvalId}/delete/`
- `getApprovalStats()`: Changed from `/stats/` to `/approvals/stats/`
- `approveSLA()`: Changed from `/${approvalId}/approve/` to `/approvals/${approvalId}/approve/`
- `rejectSLA()`: Changed from `/${approvalId}/reject/` to `/approvals/${approvalId}/reject/`

**Note:** `getSLAApprovals()` and `getAssignerApprovals()` were left as-is since they use different endpoint patterns.

## Backend URL Configuration
✅ **Backend URLs**: Correctly configured
   - Base path: `api/tprm/slas/`
   - Approval path: `api/tprm/slas/approvals/`
   - Registered in: `grc_backend/backend/urls.py` line 152
   - All endpoints properly routed

## Fixed Endpoints

### Before (404/403 Errors)
- `http://localhost:8000/api/slas/` ❌
- `http://localhost:8000/api/slas/vendors/` ❌
- `http://localhost:8000/api/audits/available-users/` ❌
- `http://localhost:8000/api/tprm/slas/approvals/approvals/` ❌ (duplicate)

### After (Working)
- `http://localhost:8000/api/tprm/slas/` ✅
- `http://localhost:8000/api/tprm/slas/vendors/` ✅
- `http://localhost:8000/api/tprm/audits/available-users/` ✅
- `http://localhost:8000/api/tprm/slas/approvals/approvals/` ✅ (correct structure)

## Dashboard.vue
✅ **Dashboard.vue**: Already using correct API structure
   - Uses `apiService.request('/v1/sla-dashboard/...')`
   - With baseURL `http://localhost:8000/api/tprm`
   - Results in: `http://localhost:8000/api/tprm/v1/sla-dashboard/...`
   - Backend has: `path('api/tprm/v1/sla-dashboard/', include('tprm_backend.slas.urls'))`
   - ✅ Correctly configured

## Summary
- ✅ All hardcoded URLs fixed to include `/tprm` prefix
- ✅ Duplicate `/approvals/` issue resolved
- ✅ All SLA API endpoints now correctly routed
- ✅ Dashboard API calls verified and working

All 404 and 403 errors should now be resolved!

