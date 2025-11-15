# Synapse - Frontend

Smart Marketing Knowledge Search - Frontend Application

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```

For production, set this to your deployed backend URL (e.g., `https://your-backend.onrender.com`).

### Development

Run the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

The production build will be in the `dist` folder.

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
```

## Deployment to Vercel

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

Follow the prompts. For production deployment:
```bash
vercel --prod
```

### Option 2: Deploy via GitHub

1. Push your code to a GitHub repository

2. Go to [Vercel](https://vercel.com) and sign in with GitHub

3. Click "New Project" and import your repository

4. Configure environment variables:
   - Add `VITE_API_BASE_URL` with your backend API URL (e.g., `https://your-backend.onrender.com`)

5. Click "Deploy"

Vercel will automatically deploy on every push to your main branch.

## Environment Variables

- `VITE_API_BASE_URL` - The base URL of your FastAPI backend (default: `http://localhost:8000`)

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Main application component
│   ├── main.jsx         # React entry point
│   ├── index.css        # Global styles with Tailwind
│   └── api.js           # API service for backend communication
├── index.html           # HTML entry point
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind CSS configuration
└── postcss.config.js    # PostCSS configuration
```

## Features

- **Semantic Search**: Natural language query interface
- **Real-time Results**: Instant search with loading states
- **Result Cards**: Display source files, content chunks, and similarity scores
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: User-friendly error messages

## API Integration

The frontend communicates with the FastAPI backend via the `/search` endpoint:

**POST /search**
```json
{
  "query": "What were our Q3 campaign results?"
}
```

**Response:**
```json
[
  {
    "id": "uuid",
    "content": "The campaign results for Q3 showed...",
    "source": "Q3_Report.pdf",
    "similarity": 0.89
  }
]
```


