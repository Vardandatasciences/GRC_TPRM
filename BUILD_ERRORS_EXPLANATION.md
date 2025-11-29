# Build Errors Explanation & Fix

## 🔴 What Are These Errors?

The errors you're seeing are **build/compilation errors** when trying to integrate TPRM components into GRC. Here's what they mean:

### **Error Categories:**

#### 1. **TypeScript Syntax Errors** (Most Common)
```
ERROR: Module parse failed: Unexpected token (133:27)
export function render(_ctx: any,_cache: any,$props: any,...)
```

**Problem**: 
- TPRM components use **TypeScript** (`.ts` files, type annotations like `: any`)
- GRC uses **Vue CLI with Babel** (no TypeScript support by default)
- When webpack tries to compile TPRM components, it can't parse TypeScript syntax

**Why**: TPRM was built with **Vite + TypeScript**, but GRC uses **Vue CLI + Babel**

---

#### 2. **Missing Dependencies**
```
ERROR: Module not found: Error: Can't resolve 'pinia'
```

**Problem**: 
- TPRM components use `pinia` for state management
- GRC doesn't have `pinia` installed (uses Vuex instead)

---

#### 3. **ESLint Parsing Errors**
```
ERROR: Parsing error: Unexpected token, expected ","
```

**Problem**: 
- ESLint is trying to lint TPRM files
- TPRM files have TypeScript syntax that ESLint (configured for JavaScript) can't parse

---

## ✅ Solutions Applied

### **1. Updated `vue.config.js`**
- Added TypeScript support for TPRM files
- Configured webpack to transpile TPRM dependencies
- Excluded TPRM from ESLint during build

### **2. Updated `babel.config.js`**
- Added `@babel/preset-typescript` to handle TypeScript files

### **3. Updated `package.json`**
- Added `pinia` dependency
- Added `@babel/preset-typescript` dev dependency
- Added `typescript` dev dependency

---

## 📋 Next Steps

### **Step 1: Install Dependencies**
```bash
cd grc_frontend
npm install
```

This will install:
- `pinia` (for TPRM state management)
- `@babel/preset-typescript` (for TypeScript support)
- `typescript` (TypeScript compiler)

### **Step 2: Rebuild**
```bash
npm run serve
# or
npm run build
```

### **Step 3: If Errors Persist**

If you still see TypeScript errors, we may need to:

**Option A**: Configure webpack to ignore TypeScript syntax in compiled templates
**Option B**: Pre-compile TPRM components separately
**Option C**: Use a different import strategy

---

## 🔍 Understanding the Error Messages

### **Format:**
```
ERROR in ./tprm_frontend/src/pages/BCP/QuestionnaireAssignment.vue
Module parse failed: Unexpected token (133:27)
```

**Breaking it down:**
- `ERROR in` - Error location
- `./tprm_frontend/src/pages/BCP/QuestionnaireAssignment.vue` - The file causing the error
- `Module parse failed` - Webpack can't parse/compile this file
- `Unexpected token (133:27)` - Line 133, column 27 has unexpected syntax
- `export function render(_ctx: any,...)` - The TypeScript syntax causing the issue

---

## 🛠️ Alternative Solutions

If the build configuration doesn't fully resolve the issues, we can:

1. **Copy TPRM components to GRC** (instead of importing from separate folder)
2. **Build TPRM separately** and import as compiled modules
3. **Use iframe/micro-frontend** approach (more complex)
4. **Convert TPRM components** to JavaScript (time-consuming)

---

## 📝 Summary

**Root Cause**: Build system mismatch
- **TPRM**: Vite + TypeScript
- **GRC**: Vue CLI + Babel

**Solution**: Configure GRC build to handle TypeScript and TPRM dependencies

**Status**: Configuration updated, need to install dependencies and rebuild


