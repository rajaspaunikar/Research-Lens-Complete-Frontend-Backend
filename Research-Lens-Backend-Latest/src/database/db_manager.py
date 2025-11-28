import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import random
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, text, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import insert as pg_insert

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:newpassword@localhost:5432/research_lens")
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Paper(Base):
    __tablename__ = "papers"
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    abstract = Column(Text)
    authors = Column(JSON)
    categories = Column(JSON)
    primary_category = Column(String, index=True)
    published_date = Column(DateTime, index=True)
    updated_date = Column(DateTime)
    pdf_url = Column(Text)
    pdf_path = Column(Text)
    comment = Column(Text)
    scraped_at = Column(DateTime, default=datetime.now)
    readability_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    keywords = relationship("Keyword", back_populates="paper", cascade="all, delete-orphan")
    findings = relationship("KeyFinding", back_populates="paper", cascade="all, delete-orphan")

class Keyword(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    keyword = Column(String, index=True, nullable=False)
    frequency = Column(Integer)
    paper = relationship("Paper", back_populates="keywords")

class KeyFinding(Base):
    __tablename__ = "key_findings"
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id", ondelete="CASCADE"))
    finding_text = Column(Text)
    finding_type = Column(String)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    paper = relationship("Paper", back_populates="findings")

class DatabaseManager:
    def __init__(self):
        Base.metadata.create_all(bind=engine)

    def get_session(self):
        return SessionLocal()

    def insert_paper(self, data):
        s = self.get_session()
        try:
            q = pg_insert(Paper).values(
                arxiv_id=data['arxiv_id'],
                title=data['title'],
                abstract=data['abstract'],
                authors=data.get('authors', []),
                categories=data.get('categories', []),
                primary_category=data.get('primary_category', ''),
                published_date=data['published_date'],
                updated_date=data['updated_date'],
                pdf_url=data.get('pdf_url', ''),
                comment=data.get('comment', ''),
                scraped_at=datetime.now()
            )
            q = q.on_conflict_do_update(
                index_elements=['arxiv_id'],
                set_={
                    'updated_date': q.excluded.updated_date,
                    'pdf_url': q.excluded.pdf_url
                }
            ).returning(Paper.id)
            
            res = s.execute(q)
            s.commit()
            return res.scalar()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()

    def insert_keywords(self, pid, k_list):
        s = self.get_session()
        try:
            objs = [Keyword(paper_id=pid, keyword=k, frequency=f) for k, f in k_list]
            s.add_all(objs)
            s.commit()
        except:
            s.rollback()
        finally:
            s.close()

    def insert_key_findings(self, pid, f_data):
        if not f_data or f_data.get('score', 0) <= 0:
            return
        s = self.get_session()
        try:
            obj = KeyFinding(
                paper_id=pid,
                finding_text=f_data['text'],
                finding_type=f_data['type'],
                score=f_data['score']
            )
            s.add(obj)
            s.commit()
        except:
            s.rollback()
        finally:
            s.close()

    def get_dashboard_findings(self, limit=10):
        s = self.get_session()
        try:
            rows = s.query(KeyFinding, Paper)\
                .join(Paper, KeyFinding.paper_id == Paper.id)\
                .order_by(desc(Paper.published_date))\
                .limit(limit)\
                .all()

            data = []
            for f, p in rows:
                prio = "high" if f.score >= 5 else "medium"
                ntype = "success" if f.score >= 5 else "info"
                data.append({
                    "id": f"finding-{f.id}",
                    "title": f"{f.finding_type}: {p.title[:30]}...",
                    "message": f.finding_text,
                    "timestamp": p.published_date.isoformat(),
                    "type": ntype,
                    "priority": prio,
                    "read": False
                })
            return data
        finally:
            s.close()

    def get_trending_topics(self, days=7, top_n=20):
        s = self.get_session()
        try:
            date_limit = datetime.now() - timedelta(days=days)
            q = s.query(Keyword.keyword, func.count(Keyword.id).label('cnt'))\
                 .join(Paper)\
                 .filter(Paper.published_date >= date_limit)\
                 .group_by(Keyword.keyword)\
                 .order_by(desc('cnt'))\
                 .limit(top_n)
            return [{"keyword": r[0], "count": r[1]} for r in q.all()]
        finally:
            s.close()

    def search_papers(self, keyword=None, category=None, start_date=None, limit=100):
        s = self.get_session()
        try:
            q = s.query(Paper)
            if keyword:
                term = f"%{keyword}%"
                q = q.filter(
                    (Paper.title.ilike(term)) | 
                    (Paper.abstract.ilike(term)) |
                    (Paper.arxiv_id.ilike(term))
                )
            if category:
                q = q.filter(Paper.primary_category == category)
            if start_date:
                q = q.filter(Paper.published_date >= start_date)

            # USE THE VARIABLE 'limit' HERE INSTEAD OF HARDCODED 100
            rows = q.order_by(desc(Paper.published_date)).limit(limit).all()
            
            res = []
            for p in rows:
                res.append({
                    "id": p.id,
                    "arxiv_id": p.arxiv_id,
                    "title": p.title,
                    "abstract": p.abstract,
                    "authors": p.authors,
                    "categories": p.categories,
                    "primary_category": p.primary_category,
                    "published_date": p.published_date.isoformat() if p.published_date else None,
                    "pdf_url": p.pdf_url,
                    "pdf_path": p.pdf_path,
                    "is_downloaded": bool(p.pdf_path)
                })
            return res
        finally:
            s.close()

    def get_chart_analytics(self):
        s = self.get_session()
        try:
            out = {"week": [], "month": [], "year": []}
            
            q_week = text("""
                SELECT 
                    TO_CHAR(published_date, 'MM/DD') as date,
                    COUNT(id) as papers_indexed,
                    SUM(CASE WHEN pdf_path IS NOT NULL THEN 1 ELSE 0 END) as downloads,
                    (SELECT COUNT(*) FROM key_findings k WHERE k.paper_id = papers.id) as ai_insights
                FROM papers
                WHERE published_date >= NOW() - INTERVAL '7 days'
                GROUP BY date, published_date::date
                ORDER BY published_date::date ASC
            """)
            out["week"] = [dict(row._mapping) for row in s.execute(q_week)]

            q_month = text("""
                SELECT 
                    TO_CHAR(published_date, 'YYYY-MM') as date_raw,
                    TO_CHAR(published_date, 'Mon') as date,
                    COUNT(id) as papers_indexed,
                    SUM(CASE WHEN pdf_path IS NOT NULL THEN 1 ELSE 0 END) as downloads,
                    (SELECT COUNT(*) FROM key_findings k WHERE k.paper_id = papers.id) as ai_insights
                FROM papers
                WHERE published_date >= NOW() - INTERVAL '12 months'
                GROUP BY date_raw, date
                ORDER BY date_raw ASC
            """)
            out["month"] = [dict(row._mapping) for row in s.execute(q_month)]

            q_year = text("""
                SELECT 
                    TO_CHAR(published_date, 'YYYY') as date,
                    COUNT(id) as papers_indexed,
                    SUM(CASE WHEN pdf_path IS NOT NULL THEN 1 ELSE 0 END) as downloads,
                    (SELECT COUNT(*) FROM key_findings k WHERE k.paper_id = papers.id) as ai_insights
                FROM papers
                GROUP BY date
                ORDER BY date ASC
            """)
            out["year"] = [dict(row._mapping) for row in s.execute(q_year)]

            return out
        finally:
            s.close()

    def get_keyword_trends(self, keys, d=30):
        if not keys:
            return []
        s = self.get_session()
        try:
            q = text(f"""
                SELECT 
                    TO_CHAR(p.published_date, 'YYYY-MM-DD') as date_label,
                    k.keyword,
                    COUNT(*) as count
                FROM keywords k
                JOIN papers p ON k.paper_id = p.id
                WHERE k.keyword IN :k_list
                  AND p.published_date >= NOW() - INTERVAL '{d} days'
                GROUP BY date_label, k.keyword
                ORDER BY date_label ASC
            """)
            res = s.execute(q, {"k_list": tuple(keys)})
            return [dict(row._mapping) for row in res]
        finally:
            s.close()
