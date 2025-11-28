import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re



class ArxivScraper:
    def __init__(self):
        self.base_url = "https://arxiv.org/search/advanced" #setting base url for advance searching
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:145.0) Gecko/20100101 Firefox/145.0'#user agent setting
        }




    #function accepts a start and  end date if not passed uses default date must be in yyyy-mm-dd format
    def scrape_date_range(self, start_date="2025-11-20", end_date="2025-11-23"):
        papers = []
        current_start = 0
        page_size = 50 # arxiv has 50 pages per page in the advance search .that we are using 

        print("Starting Advanced Scrape: {start_date} to {end_date}") # just prints the search range
        print("Target URL: {self.base_url}") # and url it searching for 
        
        # parameters matching our target or provided link exactly
        base_params = {
            'advanced': '',
            'terms-0-operator': 'AND',
            'terms-0-term': '',  # Empty term = "All papers"
            'terms-0-field': 'title',
            'classification-computer_science': 'y',
            'classification-physics_archives': 'all',
            'classification-include_cross_list': 'include',
            'date-year': '',
            'date-filter_by': 'date_range',
            'date-from_date': start_date,
            'date-to_date': end_date,
            'date-date_type': 'submitted_date',
            'abstracts': 'show',
            'size': str(page_size),
            'order': 'announced_date_first'
        }




        while True:
            # Update pagination start index
            base_params['start'] = current_start
            
            try:
                # page fetch
                print(f"   Fetching results {current_start} - {current_start + page_size}...")
                #just a delay to not spamm the arxiv server
                time.sleep(2)
                
                resp = requests.get(self.base_url, params=base_params, headers=self.headers) #response  getting
                
                if resp.status_code != 200:# ie, if not success
                    print(f"Error: Status {resp.status_code}")
                    break

                # parse the respose using html parser and cearte bs4 object
                soup = BeautifulSoup(resp.text, 'html.parser')
                results = soup.find_all('li', class_='arxiv-result')

                if not results:
                    print("No more results found. Scrape finished.")
                    break
                #data extraction
                for item in results:
                    try:
                        #title
                        title_tag = item.find('p', class_='title')
                        title = title_tag.text.replace('Title:', '').strip() if title_tag else "No Title"

                        #link
                        link_tag = item.find('p', class_='list-title').find('a')
                        arxiv_url = link_tag['href']
                        arxiv_id = arxiv_url.split('/')[-1]
                        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

                        #abstract
                        abstract = ""
                        abs_full = item.find('span', class_='abstract-full')
                        if abs_full:
                            abstract = abs_full.text.replace('Abstract:', '').replace('∆ Less', '').strip()
                        else:
                            abs_short = item.find('span', class_='abstract-short')
                            if abs_short:
                                abstract = abs_short.text.replace('Abstract:', '').strip()

                        #author
                        authors = []
                        auth_tag = item.find('p', class_='authors')
                        if auth_tag:
                            auth_text = auth_tag.text.replace('Authors:', '').strip()
                            authors = [a.strip() for a in auth_text.split(',')]

                        #categories
                        tags_div = item.find('div', class_='tags')
                        tags = []
                        primary_cat = "cs.AI"
                        if tags_div:
                            tag_spans = tags_div.find_all('span', class_='tag')
                            tags = [t.text for t in tag_spans]
                            if tags:
                                primary_cat = tags[0]

                        #date avanced search results usually show submitted X or announced x we'll use current date as scraped_at, and try to parse published
                        pub_date = datetime.now() #default
                        date_p = item.find('p', class_='is-size-7')
                        if date_p:
                            date_text = date_p.text.strip()
                            # Try to find "submitted 'date'"
                            match = re.search(r'submitted\s+(.*?)(;|\.|$)', date_text, re.IGNORECASE)
                            if match:
                                d_str = match.group(1).strip()
                                try:
                                    pub_date = datetime.strptime(d_str, "%d %B, %Y")
                                except:
                                    pass
                        paper = {# everything to this collected
                            'arxiv_id': arxiv_id,
                            'title': title,
                            'authors': authors,
                            'abstract': abstract,
                            'categories': tags,
                            'primary_category': primary_cat,
                            'published_date': pub_date,
                            'updated_date': pub_date,
                            'pdf_url': pdf_url,
                            'comment': None,
                            'scraped_at': datetime.now()
                        }
                        papers.append(paper)# and append to papers

                    except Exception as e:
                        print(f"   Skipping item error: {e}")
                        continue

                #go to Next Page
                current_start += page_size
                
                #sanity check: If we get less results than page size, we are finished then
                if len(results) < page_size:
                    print("Reached last page.")
                    break

            except Exception as e:
                print(f"Critical Error: {e}")
                break
        
        print(f"Total Papers Scraped: {len(papers)}")
        return papers
    



    def download_pdf(self, pdf_url, save_path):
        #same download logic as before
        try:
            r = requests.get(pdf_url, stream=True, timeout=30, headers=self.headers)
            if r.status_code == 200:
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        f.write(chunk)
                return True
            return False
        except:
            return False