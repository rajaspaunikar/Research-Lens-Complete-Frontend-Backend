import React, { useEffect, useState } from 'react';
import { Activity, FileText } from 'lucide-react';

export default function Dashboard() {
  const [metrics, setMetrics] = useState([]);
  const [list, setList] = useState([]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        let res = await fetch('http://localhost:8000/api/dashboard/stats');
        let d1 = await res.json();
        setMetrics(d1);

        res = await fetch('http://localhost:8000/api/dashboard/findings');
        let d2 = await res.json();
        setList(d2);

        res = await fetch('http://localhost:8000/api/dashboard/trending-topics?days=7&top_n=5');
        let d3 = await res.json();
        setTags(d3);
      } catch (err) {
        console.log(err);
      }
    };
    loadData();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '25px' }}>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metrics.map((item, idx) => (
          <div key={idx} className="content-box" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#888', letterSpacing: '0.5px' }}>
                {item.label}
              </div>
              <div style={{ fontSize: '28px', fontWeight: 'bold', marginTop: '4px', color: '#111' }}>
                {item.value}
              </div>
              <div style={{ fontSize: '12px', color: '#aaa' }}>
                {item.description}
              </div>
            </div>
            <div style={{
              padding: '12px',
              borderRadius: '50%',
              background: item.intent === 'positive' ? '#dcfce7' : '#dbeafe',
              color: item.intent === 'positive' ? '#166534' : '#1e40af'
            }}>
              {item.icon === 'atom' ? <FileText size={24} /> : <Activity size={24} />}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <div className="content-box">
          <h3>Trending Keywords</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {tags.map((t, i) => (
              <div key={i} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px', background: '#f9fafb', borderRadius: '6px', border: '1px solid #eee'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '24px', height: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    borderRadius: '4px', fontSize: '12px', fontWeight: 'bold',
                    background: i === 0 ? '#2563eb' : '#e5e7eb',
                    color: i === 0 ? '#fff' : '#4b5563'
                  }}>
                    {i + 1}
                  </div>
                  <span style={{ fontWeight: 500, color: '#374151' }}>{t.name}</span>
                </div>
                <span style={{ fontSize: '12px', background: '#fff', padding: '2px 8px', border: '1px solid #e5e7eb', borderRadius: '4px' }}>
                  {t.points} hits
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="content-box">
          <h3>Latest Findings</h3>
          <div style={{ maxHeight: '320px', overflowY: 'auto', paddingRight: '5px' }}>
            {list.map(obj => (
              <div key={obj.id} style={{ borderBottom: '1px solid #f3f4f6', paddingBottom: '15px', marginBottom: '15px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', alignItems: 'center' }}>
                  <span className="tag-badge" style={{
                    background: obj.priority === 'high' ? '#fee2e2' : '#dbeafe',
                    color: obj.priority === 'high' ? '#991b1b' : '#1e40af'
                  }}>
                    {obj.title.split(':')[0]}
                  </span>
                  <span style={{ fontSize: '11px', color: '#9ca3af' }}>
                    {new Date(obj.timestamp).toLocaleDateString()}
                  </span>
                </div>
                <p style={{ fontSize: '14px', color: '#4b5563', lineHeight: '1.5', margin: 0 }}>
                  {obj.message}
                </p>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}