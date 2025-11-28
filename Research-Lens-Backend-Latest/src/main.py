# main.py
import sys
from scraper.scraper import ArxivScraper
from analysis.metadata_extractor import MetadataExtractor
from database.db_manager import DatabaseManager

def initial_scrape():
    """Scrape strict date range requested"""
    print("Initializing Advanced Scrape (2025-11-20 to 2025-11-23)...")
    
    scraper = ArxivScraper()
    extractor = MetadataExtractor()
    db = DatabaseManager()
    
    papers = scraper.scrape_date_range(start_date="2025-11-20", end_date="2025-11-23")
    
    print(f" Saving {len(papers)} papers to database...")
    
    for i, paper in enumerate(papers):
        if i % 50 == 0: print(f"   Processing {i}...")
        
        # 1. Clean
        paper['abstract'] = extractor.clean_abstract(paper['abstract'])
        
        # 2. Save Paper
        pid = db.insert_paper(paper)
        
        # 3. AI Analysis (Keywords/Findings)
        text = f"{paper['title']} {paper['abstract']}"
        kw = extractor.extract_keywords(text, top_n=10)
        find = extractor.extract_key_findings(paper['abstract'])
        
        db.insert_keywords(pid, kw)
        db.insert_key_findings(pid, find)

    print("Done!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'init':
        initial_scrape()
    else:
        pass