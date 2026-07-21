# AeroMind Frontend

## Project Overview

The AeroMind frontend is the operator interface for the airport operations
platform. It provides authenticated access to a live operations dashboard and
the AI assistant backed by the AeroMind Flask API.

## Tech Stack

- React 19 and TypeScript
- Vite
- React Router
- Tailwind CSS
- Lucide React icons

## Installation

From the repository root:

```bash
cd frontend
npm install
```

## Environment Variables

Copy the example frontend environment file:

```bash
cp .env.example .env
```

`VITE_API_URL` is the base URL of the Flask API. The example and the client
fallback both use:

```env
VITE_API_URL=http://localhost:5000
```

Restart the Vite development server after changing this value.

## Running Locally

Start the Flask API and PostgreSQL from the repository root as described in
the root README. Then start the frontend separately:

```bash
cd frontend
npm run dev
```

Vite serves the application at `http://localhost:5173` by default.

## Building

Create a production build in `dist/`:

```bash
cd frontend
npm run build
```

To preview that build locally:

```bash
npm run preview
```

## Folder Overview

```text
src/
├── api/          API client and JWT request handling
├── components/   Shared route and UI components
├── context/      Authentication state
├── pages/        Login, registration, dashboard and chat views
├── types/        API response types
├── App.tsx       Application routes
└── main.tsx      React entry point
```

## Main Pages

- **Login and Register** (`/login`, `/register`) authenticate users and store
  the returned JWT in browser local storage.
- **Dashboard** (`/`) summarizes flights, gates, incidents and the latest
  weather report. It requires authentication.
- **AI Chat** (`/chat`) sends questions to the agent, continues or deletes
  saved conversations, and displays the tools used for each new answer. It
  requires authentication.

## API Communication

`src/api/client.ts` sends JSON requests to `VITE_API_URL`. When a user is
signed in, it adds the stored JWT as a Bearer token. The dashboard reads
`/flights`, `/gates`, `/incidents` and `/weather`; authentication uses
`/auth/register`, `/auth/login` and `/auth/me`; chat and history use
`/agent/query` and `/agent/conversations`.

Non-success responses are converted to `ApiError` instances. A `401` response
clears the stored token so protected pages return the user to login.
