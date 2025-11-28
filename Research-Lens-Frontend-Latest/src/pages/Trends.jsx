import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { X } from 'lucide-react';

export default function Trends() {
  const [chartData, setChartData] = useState([]);
  const [val, setVal] = useState("");
  const [tags, setTags] = useState(["llm", "transformer"]);

  const colors = ['#2563eb', '#e11d48', '#16a34a', '#d97706', '#9333ea'];

  useEffect(() => {
    if (tags.length === 0) {
      setChartData([]);
      return;
    }

    const getTrends = async () => {
      try {
        const url = `http://localhost:8000/api/analytics/keyword-trends?keywords=${tags.join(',')}`;
        const response = await fetch(url);
        const res = await response.json();
        setChartData(res);
      } catch (e) {
        console.log("error fetching trends", e);
      }
    };

    getTrends();
  }, [tags]);

  const handleAdd = () => {
    if (val && !tags.includes(val)) {
      setTags([...tags, val]);
      setVal("");
    }
  };

  const handleRemove = (t) => {
    const newTags = tags.filter(x => x !== t);
    setTags(newTags);
  };

  return (
    <div className="content-box" style={{ height: 'calc(100vh - 140px)', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
        <div>
          <h3 style={{ border: 'none', marginBottom: '5px', textTransform: 'none', fontSize: '18px' }}>
            Keyword Velocity Analysis
          </h3>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: 0 }}>
            Compare research interest over the last 30 days.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            className="search-input"
            style={{ width: '200px' }}
            placeholder="e.g. diffusion"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
          />
          <button className="action-button" onClick={handleAdd}>Add</button>
        </div>
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
        {tags.map((t, idx) => (
          <div key={t} style={{
            display: 'inline-flex', alignItems: 'center', gap: '6px',
            padding: '4px 10px', borderRadius: '20px',
            backgroundColor: '#eff6ff', color: '#1d4ed8',
            border: '1px solid #dbeafe', fontSize: '13px', fontWeight: 500
          }}>
            {t.toUpperCase()}
            <button
              onClick={() => handleRemove(t)}
              style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0, display: 'flex', color: '#1d4ed8' }}
            >
              <X size={14} />
            </button>
          </div>
        ))}
      </div>

      <div style={{ flex: 1, width: '100%', minHeight: '300px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
            <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} axisLine={false} dy={10} />
            <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }} />
            <Legend />
            {tags.map((t, i) => (
              <Line
                key={t}
                type="monotone"
                dataKey={t}
                stroke={colors[i % colors.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}