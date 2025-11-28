# Research Lens - Dashboard UI

A clean, responsive, and lightweight Single Page Application (SPA) built to visualize research trends and manage paper repositories. This frontend connects to the **Research Lens** Python backend to provide an interactive interface for researchers.

---

## Project Structure


.
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── postcss.config.js
├── public
├── README.md
├── src
│   ├── App.jsx
│   ├── index.css
│   ├── main.jsx
│   └── pages
│       ├── Dashboard.jsx    # Stats, Top Keywords, Latest Findings, Impact Metrics
│       ├── Repository.jsx
│       └── Trends.jsx
├── tailwind.config.js
└── vite.config.js

4 directories, 14 files
```
src/
├── pages/              
│   ├── Dashboard.jsx  
│   ├── Repository.jsx  
│   └── Trends.jsx      # Interactive Keyword Velocity Graph
├── App.jsx             # Main Routing & Layout configuration
└── index.css           # Custom styling & Tailwind imports
```

---

## Tech Stack

- **Core:** React.js, Vite  
- **Routing:** React Router DOM  
- **Styling:** Tailwind CSS (via PostCSS) + Custom CSS modules  
- **Charts & Visualization:** Recharts  
- **Icons:** Lucide React  

---

## Key Features

- **Interactive Dashboard**  
  High-level metrics, latest findings, and keyword insights.

- **Advanced Search**  
  Instant indexing, autocomplete, and filtering by keyword, authors, timeline, and citations.

- **Trend Visualization**  
  Compare keyword velocity over time (e.g., _LLMs_ vs _Diffusion Models_) using real–time interactive graphs.

- **Paper Repository**  
  Organized table view with ability to sort, filter, and download research PDFs.

- **Mobile Friendly**  
  Fully responsive layout for tablets and mobile devices.

- **Collaboration (Planned)**  
  Notes, tagging, bookmarking, and shared curated lists.

- **Offline Access**  
  Access locally downloaded papers even without backend connectivity.

---

## Getting Started

### 1️ Prerequisites

- Node.js `v16+`  
- Backend API running at: `http://localhost:8000`

---

### 2️ Installation

Run the following:

```bash
npm install
```

---

### 3️ Start Dev Server

```bash
npm run dev
```

Open in browser:

```
http://localhost:5173
```