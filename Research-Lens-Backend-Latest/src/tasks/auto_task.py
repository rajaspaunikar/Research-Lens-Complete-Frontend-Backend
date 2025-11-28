from celery import Celery
from celery.schedules import crontab

#initialize celery named research lens which using redis message broker ie, the background task are stored in redis and executed from queue
app = Celery('research_lens', broker='redis://localhost:6379/0')

# basically background scheduler like cron
app.conf.beat_schedule = {
    'scrape-papers-daily': {
        'task': 'tasks.celery_tasks.scrape_and_process',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    }}

@app.task
def scrape_and_process():#scrape new papers and process them

    from scraper.arxiv_scraper import ArxivScraper
    from analysis.metadata_extractor import MetadataExtractor
    from database.db_manager import DatabaseManager
    
    scraper = ArxivScraper(categories=['cs.AI', 'cs.LG', 'cs.CV', 'cs.NE'])
    extractor = MetadataExtractor()
    db = DatabaseManager()
        
    papers = scraper.scrape_recent_papers(days_back=1, max_results=100)#scrape papers
    
    processed_count = 0
    for paper in papers:
        
        paper['abstract'] = extractor.clean_abstract(paper['abstract'])#clean abstract
        
        paper_id = db.insert_paper(paper)#insert paper
           
        text = f"{paper['title']} {paper['abstract']}"#extract and insert keywords
        keywords = extractor.extract_keywords(text, top_n=15)
        db.insert_keywords(paper_id, keywords)
        
        processed_count += 1
    
    return f"Processed {processed_count} papers"
