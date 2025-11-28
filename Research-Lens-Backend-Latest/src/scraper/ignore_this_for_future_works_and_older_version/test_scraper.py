from scraper import ArxivScraper
import json

def main():
    scraper = ArxivScraper()
    papers = scraper.scrape_date_range("2025-11-20", "2025-11-23")

    print("Scraping Completed")
    print(f"Total papers scraped: {len(papers)}")

    if papers:
        print("\nSample Paper:")
        print(json.dumps(papers[0], indent=4, default=str))

    if papers:
        first_pdf = papers[0]['pdf_url']
        print("\nDownloading first PDF...")
        saved = scraper.download_pdf(first_pdf, "sample.pdf")
        print("PDF saved:", saved)

if __name__ == "__main__":
    main()
