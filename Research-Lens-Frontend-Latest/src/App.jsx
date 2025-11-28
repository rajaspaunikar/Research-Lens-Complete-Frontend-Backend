import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Repository from './pages/Repository';
import Trends from './pages/Trends';
import { LayoutGrid, FileText, TrendingUp } from 'lucide-react';

function TopBar() {
  const loc = useLocation();
  const p = loc.pathname;

  return (
    <nav style={{ background: '#fff', borderBottom: '1px solid #e5e7eb', position: 'sticky', top: 0, zIndex: 100 }}>
      <div className="app-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span style={{ fontWeight: 700, fontSize: '18px', letterSpacing: '-0.5px' }}>Research Lens</span>
        </div>
        
        <div style={{ display: 'flex', gap: '5px' }}>
          <Link to="/" className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${p === '/' ? 'text-blue-600 bg-blue-50 font-semibold' : 'text-gray-600 hover:bg-gray-100'}`}>
            <LayoutGrid size={18} /> Dashboard
          </Link>
          
          <Link to="/repository" className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${p === '/repository' ? 'text-blue-600 bg-blue-50 font-semibold' : 'text-gray-600 hover:bg-gray-100'}`}>
            <FileText size={18} /> Repository
          </Link>
          
          <Link to="/trends" className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${p === '/trends' ? 'text-blue-600 bg-blue-50 font-semibold' : 'text-gray-600 hover:bg-gray-100'}`}>
            <TrendingUp size={18} /> Trends
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa' }}>
        <TopBar />
        <main className="app-container" style={{ padding: '24px 20px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/repository" element={<Repository />} />
            <Route path="/trends" element={<Trends />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}