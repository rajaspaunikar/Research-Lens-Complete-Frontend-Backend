import pandas as pd
from datetime import datetime, timedelta

class TrendAnalyzer:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def analyze_keyword_trends(self, days=30):
        conn = self.db.engine.connect()
        try:
            query = """
                SELECT 
                    k.keyword,
                    DATE(p.published_date) as date,
                    COUNT(*) as count
                FROM keywords k
                JOIN papers p ON k.paper_id = p.id
                WHERE p.published_date >= NOW() - INTERVAL '%s days'
                GROUP BY k.keyword, DATE(p.published_date)
                ORDER BY date, count DESC
            """
            return pd.read_sql_query(query % days, conn)
        finally:
            conn.close()
    
    def get_category_distribution(self):
        conn = self.db.engine.connect()
        try:
            query = """
                SELECT primary_category, COUNT(*) as count
                FROM papers
                GROUP BY primary_category
                ORDER BY count DESC
            """
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()
    
    def get_papers_per_day(self, days=30):
        conn = self.db.engine.connect()
        try:
            query = """
                SELECT 
                    DATE(published_date) as date,
                    COUNT(*) as count
                FROM papers
                WHERE published_date >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(published_date)
                ORDER BY date
            """
            return pd.read_sql_query(query % days, conn)
        finally:
            conn.close()
    
    def detect_emerging_topics(self, window=7, threshold=5):
        current_data = self.db.get_trending_topics(days=window, top_n=100)
        
        s = self.db.get_session()
        try:
            # Manual query for previous period comparison
            # Postgres syntax: NOW() - INTERVAL 'X days'
            prev_start = window * 2
            
            q = f"""
                SELECT k.keyword, COUNT(*) 
                FROM keywords k
                JOIN papers p ON k.paper_id = p.id
                WHERE p.published_date >= NOW() - INTERVAL '{prev_start} days'
                  AND p.published_date < NOW() - INTERVAL '{window} days'
                GROUP BY k.keyword
            """
            
            res = s.execute(text(q))
            prev_counts = {row[0]: row[1] for row in res}
            
            emerging = []
            
            for item in current_data:
                kw = item['keyword']
                curr_count = item['count']
                prev_count = prev_counts.get(kw, 0)
                
                rate = 0.0
                if prev_count == 0 and curr_count >= threshold:
                    rate = 100.0
                elif prev_count > 0:
                    rate = (curr_count - prev_count) / prev_count
                
                if rate > 0.5:
                    emerging.append({
                        'keyword': kw,
                        'current_count': curr_count,
                        'previous_count': prev_count,
                        'growth_rate': rate
                    })
            
            return sorted(emerging, key=lambda x: x['growth_rate'], reverse=True)
            
        finally:
            s.close()