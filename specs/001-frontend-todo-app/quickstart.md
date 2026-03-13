# Quickstart Guide: Frontend Todo Application

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git version control
- A backend API running with authentication endpoints

## Setup Instructions

### 1. Clone and Install Dependencies

```bash
git clone <repository-url>
cd frontend
npm install
```

### 2. Environment Configuration

Create a `.env.local` file in the root of the frontend directory:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_JWT_SECRET=your-jwt-secret-key
NEXT_PUBLIC_APP_NAME=Todo App
```

### 3. Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Key Features Walkthrough

### Authentication Flow
1. Visit `/signup` to create a new account
2. Use `/signin` to log in with existing credentials
3. Authenticated users are redirected to `/dashboard`
4. Session is maintained via JWT tokens

### Task Management
1. On the dashboard, view existing tasks in the task list
2. Click "Add Task" to create a new task
3. Toggle task completion with the checkbox
4. Edit or delete tasks using the action buttons

### Responsive Design
- Mobile: Single column layout with touch-friendly controls
- Tablet: Two-column layout for better space utilization
- Desktop: Full-width dashboard with expanded controls

## Common Commands

```bash
# Development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test

# Lint code
npm run lint

# Format code
npm run format
```

## Troubleshooting

### Authentication Issues
- Ensure backend API is running and accessible
- Verify JWT secret matches between frontend and backend
- Clear browser cache if experiencing session issues

### API Connection Problems
- Check `NEXT_PUBLIC_API_BASE_URL` in environment variables
- Verify CORS settings on the backend
- Confirm all required headers are being sent

### Styling Problems
- Ensure Tailwind CSS is properly configured
- Check for conflicting CSS rules
- Verify responsive breakpoints are correctly implemented