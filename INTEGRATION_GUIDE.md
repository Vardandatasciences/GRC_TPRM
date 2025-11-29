# GRC + TPRM Integration Guide
## Unified Login & Sidebar Integration

This guide provides step-by-step instructions to integrate TPRM modules into GRC's sidebar while maintaining separate backends and databases.

---

## 📋 Overview

**Goal**: Use GRC's login page, home page, and sidebar UI, and add all TPRM modules to the GRC sidebar.

**Architecture**:
- **Frontend**: GRC frontend (Vue.js) with unified sidebar
- **Backend**: Separate backends (GRC Django + TPRM backend)
- **Database**: Separate databases (no changes needed)
- **Authentication**: GRC authentication system (shared users)

---

## 🎯 Step-by-Step Implementation Plan

### **Phase 1: Analysis & Preparation**

#### Step 1.1: Identify TPRM Modules
From the TPRM codebase, identify all modules:
- ✅ **Vendor Management** (`/vendor-*`)
- ✅ **Contract Management** (`/contract*`)
- ✅ **RFP Management** (`/rfp-*`)
- ✅ **BCP/DRP** (`/bcp/*`)
- ✅ **SLA Management** (`/slas`, `/sla-*`)

#### Step 1.2: Map TPRM Routes
Document all TPRM routes from:
- `Tprm/src/router/index.js` (main router)
- `Tprm/src/router/index_vendor.js`
- `Tprm/src/router/index_rfp.js`
- `Tprm/src/router/index_contract.js`
- `Tprm/src/router/index_bcp.js`

#### Step 1.3: Identify API Endpoints
- GRC Backend: `UI_GRC/backend/`
- TPRM Backend: `Tprm/backend/`
- Note API base URLs for configuration

---

### **Phase 2: Frontend Integration**

#### Step 2.1: Copy TPRM Components to GRC Frontend
**Action**: Copy TPRM components that will be used in GRC routes

```bash
# Create TPRM module directories in GRC frontend
UI_GRC/frontend/src/components/TPRM/
├── Vendor/
├── Contract/
├── RFP/
├── BCP/
└── SLA/
```

**OR** (Recommended): Keep TPRM components in TPRM folder and import them via path aliases.

#### Step 2.2: Update GRC Router
**File**: `UI_GRC/frontend/src/router/index.js`

**Action**: Add TPRM routes to GRC router

1. Import TPRM components (lazy loading recommended)
2. Add routes for each TPRM module
3. Use route prefixes to avoid conflicts:
   - `/tprm/vendor/*` for vendor routes
   - `/tprm/contract/*` for contract routes
   - `/tprm/rfp/*` for RFP routes
   - `/tprm/bcp/*` for BCP routes
   - `/tprm/sla/*` for SLA routes

**Example Route Addition**:
```javascript
// Vendor Management Routes
{
  path: '/tprm/vendor-dashboard',
  name: 'TPRMVendorDashboard',
  component: () => import('@/components/TPRM/Vendor/VendorDashboard.vue'),
  meta: { requiresAuth: true }
},
// ... more routes
```

#### Step 2.3: Update GRC Sidebar
**File**: `UI_GRC/frontend/src/components/Policy/Sidebar.vue`

**Action**: Add TPRM module sections to sidebar

1. Add new menu sections for TPRM modules
2. Structure similar to existing Policy/Compliance sections
3. Use collapsible submenus for better organization

**Example Sidebar Addition**:
```vue
<!-- TPRM Section -->
<div @click="toggleSubmenu('tprm')" class="menu-item has-submenu" :class="{'expanded': openMenus.tprm}">
  <i class="fas fa-building icon"></i>
  <span v-if="!isCollapsed">TPRM</span>
  <i v-if="!isCollapsed" class="fas fa-chevron-right submenu-arrow"></i>
</div>
<div v-if="!isCollapsed && openMenus.tprm" class="submenu">
  <!-- Vendor Management -->
  <div @click="toggleSubmenu('vendor')" class="menu-item has-submenu" :class="{'expanded': openMenus.vendor}">
    <i class="fas fa-users icon"></i>
    <span>Vendor Management</span>
    <i class="fas fa-chevron-right submenu-arrow"></i>
  </div>
  <div v-if="!isCollapsed && openMenus.vendor" class="submenu">
    <div class="menu-item" @click="navigate('/tprm/vendor-dashboard')" :class="{'active': isActive('/tprm/vendor')}">
      <i class="fas fa-tachometer-alt icon"></i>
      <span>Vendor Dashboard</span>
    </div>
    <!-- More vendor sub-items -->
  </div>
  
  <!-- Contract Management -->
  <!-- RFP Management -->
  <!-- BCP Management -->
  <!-- SLA Management -->
</div>
```

#### Step 2.4: Configure API Services
**File**: `UI_GRC/frontend/src/config/api.js` or create new `tprmApi.js`

**Action**: Configure API endpoints for TPRM backend

```javascript
// TPRM API Configuration
export const TPRM_API_BASE_URL = process.env.VITE_TPRM_API_BASE_URL || 'http://localhost:8001/api'

export const tprmApiConfig = {
  baseURL: TPRM_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
}
```

#### Step 2.5: Create TPRM API Service
**File**: `UI_GRC/frontend/src/services/tprmApiService.js`

**Action**: Create service to handle TPRM API calls with GRC authentication

```javascript
import axios from 'axios'
import { tprmApiConfig } from '@/config/tprmApi'
import authService from './authService'

const tprmApi = axios.create(tprmApiConfig)

// Add request interceptor to include GRC auth token
tprmApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Add response interceptor for error handling
tprmApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
      await authService.refreshAccessToken()
    }
    return Promise.reject(error)
  }
)

export default tprmApi
```

---

### **Phase 3: Backend Integration**

#### Step 3.1: Configure CORS (TPRM Backend)
**Action**: Ensure TPRM backend accepts requests from GRC frontend

- Update CORS settings in TPRM backend
- Allow GRC frontend origin
- Allow credentials if needed

#### Step 3.2: Authentication Bridge (Optional)
**Option A**: Use GRC JWT tokens directly (if both backends share JWT secret)
**Option B**: Create authentication bridge endpoint in TPRM backend

**If Option B**:
- Create endpoint: `POST /api/auth/validate-grc-token`
- Validate GRC JWT token
- Return TPRM session or token

#### Step 3.3: User Synchronization (If Needed)
**Action**: Ensure user data is accessible in both systems

- If users are in separate databases, create sync mechanism
- OR: Use shared user service/API
- OR: Map GRC user to TPRM user on first access

---

### **Phase 4: Component Integration**

#### Step 4.1: Import TPRM Components
**Options**:

**Option A**: Copy components to GRC frontend
- Pros: All code in one place
- Cons: Duplication, harder to maintain

**Option B**: Use path aliases to import from TPRM folder
- Pros: Single source of truth
- Cons: Requires proper build configuration

**Option C**: Publish TPRM as npm package
- Pros: Clean separation
- Cons: More setup complexity

**Recommended**: Option B with proper webpack/vite configuration

#### Step 4.2: Update Component Imports
**Action**: Update TPRM component imports to work with GRC structure

- Fix relative imports
- Update API service imports
- Update store/state management if needed

#### Step 4.3: Handle Styling Conflicts
**Action**: Ensure TPRM styles don't conflict with GRC styles

- Use CSS scoping
- Check for conflicting class names
- Update Tailwind/Element Plus configurations if needed

---

### **Phase 5: Testing & Validation**

#### Step 5.1: Test Authentication Flow
- ✅ Login via GRC login page
- ✅ Verify JWT token is stored
- ✅ Access GRC modules (should work as before)
- ✅ Access TPRM modules (should use GRC token)

#### Step 5.2: Test Navigation
- ✅ Sidebar shows all modules
- ✅ Clicking TPRM modules navigates correctly
- ✅ Active route highlighting works
- ✅ Breadcrumbs/navigation context works

#### Step 5.3: Test API Calls
- ✅ GRC API calls work (existing functionality)
- ✅ TPRM API calls work with GRC token
- ✅ Error handling works (401 redirects, etc.)

#### Step 5.4: Test RBAC/Permissions
- ✅ GRC permissions work as before
- ✅ TPRM permissions work (may need mapping)
- ✅ Access denied pages work correctly

---

### **Phase 6: Configuration & Environment**

#### Step 6.1: Environment Variables
**File**: `.env` or `.env.local`

```env
# GRC Backend
VITE_GRC_API_BASE_URL=http://localhost:8000/api

# TPRM Backend
VITE_TPRM_API_BASE_URL=http://localhost:8001/api

# Shared
VITE_APP_NAME=GRC+TPRM Unified Platform
```

#### Step 6.2: Build Configuration
**File**: `UI_GRC/frontend/vite.config.js` or `vue.config.js`

**Action**: Configure path aliases if importing from TPRM folder

```javascript
import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@tprm': resolve(__dirname, '../../Tprm/src') // If importing from TPRM
    }
  }
})
```

---

## 📝 Detailed Implementation Checklist

### ✅ Phase 1: Preparation
- [ ] Document all TPRM routes
- [ ] Document all TPRM API endpoints
- [ ] Identify TPRM components to integrate
- [ ] Create backup of current GRC sidebar
- [ ] Test current GRC functionality (baseline)

### ✅ Phase 2: Router Integration
- [ ] Add TPRM routes to GRC router
- [ ] Test route navigation
- [ ] Verify route guards work
- [ ] Test route parameters and query strings

### ✅ Phase 3: Sidebar Integration
- [ ] Add TPRM section to sidebar
- [ ] Add Vendor Management submenu
- [ ] Add Contract Management submenu
- [ ] Add RFP Management submenu
- [ ] Add BCP Management submenu
- [ ] Add SLA Management submenu
- [ ] Test sidebar collapse/expand
- [ ] Test active route highlighting

### ✅ Phase 4: API Integration
- [ ] Configure TPRM API base URL
- [ ] Create TPRM API service
- [ ] Add authentication interceptors
- [ ] Test API calls from TPRM components
- [ ] Handle error responses

### ✅ Phase 5: Component Integration
- [ ] Import/copy TPRM components
- [ ] Fix import paths
- [ ] Update API service references
- [ ] Test component rendering
- [ ] Fix styling conflicts

### ✅ Phase 6: Authentication
- [ ] Verify GRC login works
- [ ] Test token storage
- [ ] Test token refresh
- [ ] Verify TPRM API accepts GRC token
- [ ] Test logout (clears both)

### ✅ Phase 7: Testing
- [ ] Test all GRC modules (regression)
- [ ] Test all TPRM modules
- [ ] Test navigation between modules
- [ ] Test permissions/RBAC
- [ ] Test error handling
- [ ] Test on different browsers

### ✅ Phase 8: Documentation
- [ ] Update README
- [ ] Document new routes
- [ ] Document API configuration
- [ ] Create user guide for unified interface

---

## 🔧 Technical Considerations

### Route Naming Convention
- Use prefixes: `/tprm/*` for all TPRM routes
- Keep GRC routes as-is: `/policy/*`, `/compliance/*`, etc.

### API Configuration
- Separate API services for GRC and TPRM
- Shared authentication token
- Different base URLs

### State Management
- GRC uses Vuex (check `UI_GRC/frontend/src/store/`)
- TPRM may use Pinia or Vuex
- May need to bridge state or keep separate

### Styling
- GRC may use different CSS framework
- TPRM uses Tailwind + Element Plus
- Ensure no conflicts

### Build Process
- GRC frontend build should include TPRM components
- Or configure to import from TPRM folder
- Update build scripts if needed

---

## 🚨 Potential Issues & Solutions

### Issue 1: Route Conflicts
**Problem**: TPRM routes conflict with GRC routes
**Solution**: Use `/tprm/*` prefix for all TPRM routes

### Issue 2: Authentication Token Not Accepted
**Problem**: TPRM backend doesn't accept GRC JWT
**Solution**: 
- Share JWT secret between backends
- OR create token validation bridge
- OR implement token exchange endpoint

### Issue 3: Component Import Errors
**Problem**: TPRM components can't be imported
**Solution**: 
- Copy components to GRC folder
- OR configure path aliases
- OR use npm package

### Issue 4: Styling Conflicts
**Problem**: TPRM styles override GRC styles
**Solution**: 
- Use scoped styles
- Use CSS modules
- Update class names if needed

### Issue 5: API CORS Errors
**Problem**: CORS errors when calling TPRM API
**Solution**: Update TPRM backend CORS settings

---

## 📚 Next Steps

1. **Review this guide** and confirm approach
2. **Start with Phase 1** - Analysis and documentation
3. **Implement Phase 2** - Router integration (test incrementally)
4. **Implement Phase 3** - Sidebar integration
5. **Continue with remaining phases**

---

## 🆘 Support

If you encounter issues:
1. Check browser console for errors
2. Check network tab for API calls
3. Verify environment variables
4. Check backend logs
5. Review this guide for relevant section

---

**Ready to start?** Let's begin with Phase 1 - Analysis and Preparation!



