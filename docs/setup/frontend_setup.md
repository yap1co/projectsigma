# Frontend Setup Guide

## 📍 Location
The frontend is located in the **`client/`** directory.

## 🏗️ Frontend Stack
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query, Context API
- **Forms**: React Hook Form
- **UI Components**: Headless UI, Heroicons
- **Charts**: Recharts
- **Animations**: Framer Motion

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
cd client
npm install
```

### Step 2: Start Development Server
```bash
npm run dev
```

The frontend will run on: **http://localhost:3000**

### Step 3: Verify Backend is Running
Make sure the Flask backend is running on **http://localhost:5000**

The frontend is configured to connect to: `http://localhost:5000/api`

## 📁 Frontend Structure

```
client/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles
├── components/            # React components
│   ├── auth/             # Authentication components
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── Dashboard.tsx      # Main dashboard
│   ├── LandingPage.tsx   # Landing page
│   ├── ProfileSetup.tsx  # Profile setup
│   └── RecommendationResults.tsx
├── contexts/             # React Context providers
│   ├── AuthContext.tsx   # Authentication state
│   └── QueryContext.tsx  # React Query setup
├── lib/                  # Utilities
│   └── api.ts           # API client (axios)
├── package.json         # Dependencies
└── next.config.js       # Next.js configuration
```

## 🔧 Available Scripts

```bash
# Development
npm run dev          # Start dev server (port 3000)

# Production
npm run build        # Build for production
npm run start        # Start production server

# Testing
npm test             # Run tests
npm run test:watch   # Run tests in watch mode

# Linting
npm run lint         # Run ESLint
```

## 🌐 API Configuration

The frontend connects to the backend API. Configuration is in:
- `client/next.config.js` - Sets `NEXT_PUBLIC_API_URL`
- `client/lib/api.ts` - Axios client configuration

**Default API URL**: `http://localhost:5000/api`

## 🎯 Running Both Frontend & Backend

### Option 1: Run Separately (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd server
python app.py
```
Backend runs on: http://localhost:5000

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```
Frontend runs on: http://localhost:3000

### Option 2: Use Root Package.json Script

From project root:
```bash
npm run dev
```

This runs both server and client concurrently.

## 📱 Access the Application

Once both are running:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health

## 🔍 Frontend Features

1. **Authentication**
   - User registration
   - User login
   - JWT token management

2. **Dashboard**
   - Student profile management
   - Course recommendations
   - Results visualization

3. **Components**
   - Landing page
   - Profile setup wizard
   - Recommendation results display
   - Charts and visualizations

## ⚠️ Prerequisites

- **Node.js 18+** installed
- **npm** or **yarn** package manager
- Backend server running on port 5000

## 🐛 Troubleshooting

### "Cannot connect to API"
- Check backend is running: `curl http://localhost:5000/api/health`
- Verify `NEXT_PUBLIC_API_URL` in `next.config.js`

### "Port 3000 already in use"
- Change port: `npm run dev -- -p 3001`
- Or stop the process using port 3000

### "Module not found"
- Run: `npm install` in the `client/` directory
- Delete `node_modules` and `package-lock.json`, then reinstall

## 📚 Next Steps

1. Install frontend dependencies: `cd client && npm install`
2. Start frontend: `npm run dev`
3. Open browser: http://localhost:3000
4. Register a new user or login
5. Set up your profile
6. Get course recommendations!
