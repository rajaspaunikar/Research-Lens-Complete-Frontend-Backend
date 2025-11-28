from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uvicorn
import requests
from database.db_manager import DatabaseManager

app = FastAPI()
db = DatabaseManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def index():
    return {"status": "ok"}

@app.get("/api/papers")
def get_papers(keyword: str = None, category: str = None, start_date: str = None, limit: int = 50):
    return db.search_papers(keyword=keyword, category=category, start_date=start_date, limit=limit)

@app.get("/api/papers/{pid}")
def get_paper(pid: int):
    s = db.get_session()
    try:
        # Lazy import to avoid circular stuff
        from database.db_manager import Paper
        
        p = s.query(Paper).filter(Paper.id == pid).first()
        if not p:
            raise HTTPException(status_code=404, detail="Not found")
        
        res = {
            "id": p.id,
            "arxiv_id": p.arxiv_id,
            "title": p.title,
            "abstract": p.abstract,
            "authors": p.authors,
            "categories": p.categories,
            "primary_category": p.primary_category,
            "published_date": p.published_date,
            "pdf_url": p.pdf_url,
            "is_downloaded": bool(p.pdf_path)
        }

        res['keywords'] = [{"name": k.keyword, "count": k.frequency} for k in p.keywords]
        
        if p.findings:
            f = p.findings[0]
            res['finding'] = {
                "finding_text": f.finding_text,
                "finding_type": f.finding_type,
                "score": f.score
            }
        else:
            res['finding'] = None
            
        return res
    finally:
        s.close()

@app.get("/api/dashboard/stats")
def stats():
    s = db.get_session()
    try:
        from database.db_manager import Paper, KeyFinding
        from datetime import datetime, timedelta
        
        cnt = s.query(Paper).count()
        hi = s.query(KeyFinding).filter(KeyFinding.score >= 5).count()
        
        d7 = datetime.now() - timedelta(days=7)
        recent = s.query(Paper).filter(Paper.published_date >= d7).count()

        return [
            {
                "label": "PAPERS PARSED",
                "value": f"{cnt}",
                "description": "TOTAL DATABASE",
                "intent": "neutral",
                "icon": "atom",
                "direction": "up"
            },
            {
                "label": "HIGH IMPACT",
                "value": f"{hi}",
                "description": "SOTA & NOVEL FINDINGS",
                "intent": "positive",
                "icon": "star",
                "direction": "up"
            },
            {
                "label": "RECENT INFLUX",
                "value": f"+{recent}",
                "description": "LAST 7 DAYS",
                "intent": "neutral",
                "icon": "activity",
                "tag": "Active ⚡"
            }
        ]
    finally:
        s.close()

@app.get("/api/dashboard/trending-topics")
def trends(days: int = 7, top_n: int = 5):
    data = db.get_trending_topics(days=days, top_n=top_n)
    out = []
    for i, r in enumerate(data):
        out.append({
            "id": i + 1,
            "name": r["keyword"].title(),
            "handle": "Topic", 
            "streak": f"{r['count']} mentions", 
            "points": r["count"],
            "avatar": "/icons/hash.png" 
        })
    return out

@app.get("/api/dashboard/findings")
def findings():
    return db.get_dashboard_findings(limit=10)

@app.post("/api/papers/{pid}/download")
def download(pid: int):
    s = db.get_session()
    try:
        from database.db_manager import Paper
        p = s.query(Paper).filter(Paper.id == pid).first()
        
        if not p:
            raise HTTPException(status_code=404)
            
        url = p.pdf_url
        fname = f"{p.arxiv_id}.pdf"
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
            
        path = os.path.join("downloads", fname)
        
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
            
        p.pdf_path = path
        s.commit()
            
        return {"status": "success", "path": path}
    except Exception as e:
        s.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        s.close()

@app.get("/api/pdf/{pid}")
def view_pdf(pid: int):
    s = db.get_session()
    try:
        from database.db_manager import Paper
        p = s.query(Paper).filter(Paper.id == pid).first()
        
        if not p or not p.pdf_path or not os.path.exists(p.pdf_path):
            raise HTTPException(status_code=404)
            
        return FileResponse(p.pdf_path, media_type='application/pdf')
    finally:
        s.close()

@app.get("/api/analytics/charts")
def charts():
    return db.get_chart_analytics()

@app.get("/api/analytics/keyword-trends")
def kw_trends(keywords: str, days: int = 30):
    k_list = [x.strip().lower() for x in keywords.split(',') if x.strip()]
    raw = db.get_keyword_trends(k_list, days)
    
    mapped = {}
    for r in raw:
        d = r['date_label']
        k = r['keyword']
        v = r['count']
        
        if d not in mapped:
            mapped[d] = {"date": d}
            for x in k_list:
                mapped[d][x] = 0
        
        mapped[d][k] = v

    return sorted(mapped.values(), key=lambda z: z['date'])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)