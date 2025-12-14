# How to Use App Across Network

## Configuration Changes Made

### 1. Environment Variable Added
```
NEXT_PUBLIC_BACKEND_URL=http://localhost:5000
```

### 2. Centralized API Configuration
- Created `lib/config.ts` with all API endpoints
- All frontend files now use centralized configuration
- Replaced hardcoded `localhost:5000` URLs

## Steps to Enable Network Access

### 1. Find Your IP Address
```bash
ip addr show | grep "inet " | grep -v 127.0.0.1
```

### 2. Update .env File
```
NEXT_PUBLIC_BACKEND_URL=http://YOUR_IP_ADDRESS:5000
```
Example: `NEXT_PUBLIC_BACKEND_URL=http://192.168.1.100:5000`

### 3. Start Backend Server
```bash
flask run --host=0.0.0.0 --port=5000
```

### 4. Start Frontend
```bash
npm run dev -- --host 0.0.0.0
```

### 5. Access from Other Devices
- Frontend: `http://YOUR_IP_ADDRESS:3000`
- Backend API: `http://YOUR_IP_ADDRESS:5000`

## Benefits
- Single point of configuration
- Easy IP address changes
- Network-ready setup
- Centralized API management
