import { useEffect, useState } from 'react';
import { Download, ExternalLink, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Repository() {
  const [data, setData] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  
  const PER_PAGE = 10;

  useEffect(() => {
    const timeout = setTimeout(() => {
      getData();
    }, 500);
    return () => clearTimeout(timeout);
  }, [search]);

  const getData = async () => {
    setLoading(true);
    try {
      const url = `http://localhost:8000/api/papers?limit=1000&keyword=${search}`;
      const req = await fetch(url);
      const res = await req.json();
      setData(res);
      setPage(1);
    } catch (err) {
      console.log(err);
    }
    setLoading(false);
  };

  const dlFile = async (id) => {
    alert('Downloading...');
    await fetch(`http://localhost:8000/api/papers/${id}/download`, { method: 'POST' });
    
    const updated = data.map(item => {
      if (item.id === id) {
        return { ...item, is_downloaded: true };
      }
      return item;
    });
    setData(updated);
  };

  const total = Math.ceil(data.length / PER_PAGE);
  const start = (page - 1) * PER_PAGE;
  const viewData = data.slice(start, start + PER_PAGE);

  const next = () => {
    if (page < total) setPage(p => p + 1);
  };

  const prev = () => {
    if (page > 1) setPage(p => p - 1);
  };

  return (
    <div className="content-box">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <div className="flex items-baseline gap-2">
          <h3 style={{marginBottom: 0, border: 'none'}}>Research Repository</h3>
          <span style={{fontSize: '14px', color: '#666'}}>({data.length} found)</span>
        </div>
        
        <div className="relative w-full md:w-64">
          <input 
            type="text" 
            placeholder="Search..." 
            className="search-input pl-10"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-x-auto" style={{minHeight: '400px'}}>
        <table className="repo-table">
          <thead>
            <tr>
              <th className="w-24">ID</th>
              <th>Title</th>
              <th>Authors</th>
              <th className="w-32">Date</th>
              <th className="w-24 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="5" className="text-center py-12 text-gray-500">Loading...</td></tr>
            ) : viewData.length === 0 ? (
              <tr><td colSpan="5" className="text-center py-12 text-gray-500">No results</td></tr>
            ) : (
              viewData.map(row => (
                <tr key={row.id}>
                  <td className="font-mono text-xs text-gray-500">{row.arxiv_id}</td>
                  <td>
                    <div className="font-medium text-blue-900">{row.title}</div>
                    <div className="flex gap-2 mt-1">
                      {row.categories.slice(0, 2).map(cat => (
                        <span key={cat} style={{fontSize: '11px', background: '#f3f4f6', padding: '2px 6px', borderRadius: '4px', border: '1px solid #e5e7eb', color: '#555'}}>
                          {cat}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="text-sm text-gray-600">
                    {row.authors.length > 2 ? row.authors.slice(0, 2).join(', ') + '...' : row.authors.join(', ')}
                  </td>
                  <td className="text-sm text-gray-500 whitespace-nowrap">
                    {new Date(row.published_date).toLocaleDateString()}
                  </td>
                  <td className="text-right">
                    <div className="flex justify-end gap-2">
                      <a href={row.pdf_url} target="_blank" className="p-2 text-gray-400 hover:text-blue-600">
                        <ExternalLink size={16} />
                      </a>
                      <button 
                        onClick={() => dlFile(row.id)}
                        disabled={row.is_downloaded}
                        className="p-2 rounded"
                        style={{ color: row.is_downloaded ? 'green' : '#9ca3af' }}
                      >
                        <Download size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!loading && data.length > 0 && (
        <div className="flex items-center justify-between border-t border-gray-100 pt-4 mt-4">
          <div className="text-sm text-gray-500">
            {start + 1} - {Math.min(start + PER_PAGE, data.length)} of {data.length}
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={prev} 
              disabled={page === 1}
              className="action-button btn-outline px-3 py-1 flex items-center gap-1"
              style={{opacity: page === 1 ? 0.5 : 1}}
            >
              <ChevronLeft size={14} /> Prev
            </button>
            
            <span className="text-sm font-medium px-2">
              {page} / {total}
            </span>
            
            <button 
              onClick={next} 
              disabled={page === total}
              className="action-button btn-outline px-3 py-1 flex items-center gap-1"
              style={{opacity: page === total ? 0.5 : 1}}
            >
              Next <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}