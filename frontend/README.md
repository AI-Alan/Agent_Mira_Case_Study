# Agent Mira - AI Real Estate Chatbot

A Next.js (Pages Router) application for an AI-powered real estate chatbot that helps users find homes using dropdown-based filters.

## Features

- 🏡 Chat-based interface for property search
- 📍 Location, Budget, and Bedrooms filters
- 💾 Save properties functionality
- 🎨 Modern, responsive UI with animations
- 📱 Mobile-friendly design

## Tech Stack

- **Framework**: Next.js 16 (Pages Router)
- **Styling**: CSS Modules
- **API Client**: Axios
- **Language**: TypeScript

## Getting Started

### Prerequisites

- Node.js 18+ installed
- FastAPI backend running (see backend documentation)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env.local` file in the root directory:
```bash
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

3. Run the development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

- `NEXT_PUBLIC_API_URL` - Base URL for the FastAPI backend (default: `http://127.0.0.1:8000`)

## Project Structure

```
src/
├── pages/              # Next.js Pages Router
│   ├── _app.tsx       # App wrapper with NavBar
│   ├── _document.tsx  # HTML document structure
│   ├── index.tsx      # Home page with ChatbotUI
│   └── saved.tsx      # Saved properties page
├── components/         # React components
│   ├── ChatbotUI.tsx  # Main chatbot interface
│   ├── FilterForm.tsx # Search filters form
│   ├── PropertyCard.tsx # Property display card
│   └── NavBar.tsx     # Navigation bar
├── lib/               # Utility functions
│   └── api.ts         # API client functions
└── styles/            # CSS modules
    ├── globals.css    # Global styles
    └── *.module.css   # Component-specific styles
```

## API Endpoints

The application expects the following backend endpoints:

- `GET /properties` - Get properties with query parameters (location, budget, bedrooms)
- `POST /save` - Save a property (body: `{ user_id, property_id }`)

## Build for Production

```bash
npm run build
npm start
```

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js Pages Router](https://nextjs.org/docs/pages)
