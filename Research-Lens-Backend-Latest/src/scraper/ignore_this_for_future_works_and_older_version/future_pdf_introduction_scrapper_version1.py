import os
import re
import pdfplumber


def extract_text_by_columns(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page_num, page in enumerate(pdf.pages):#go through all pages
            width, height = page.width, page.height
        
            column_1_bbox = (0, 0, width / 2, height)  # left column bound
            column_2_bbox = (width / 2, 0, width, height)  # right column bound
            column_1_text = page.within_bbox(column_1_bbox).extract_text()#extract text from first column
            if column_1_text:
                full_text += column_1_text + "\n" 
            column_2_text = page.within_bbox(column_2_bbox).extract_text()#extract texxt from seconf column
            if column_2_text:
                full_text += column_2_text + "\n"
        return full_text

def extract_introduction_from_pdf(pdf_path):
    full_text = extract_text_by_columns(pdf_path) #extract text from entire file
    intro_regex = r"(introduction|\d+\.\s*introduction|\bINTRODUCTION\b)" #regular expression for matching
    match = re.search(intro_regex, full_text, re.IGNORECASE)
    if match:
        start_index = match.start()  # start set as intro
    else:
        return None  # no intro at all
    text_from_intro = full_text[start_index:]
    #heading_regex = r"\n([A-Z][A-Z0-9\s\.\-]+)(?=\n|\s|$)"# for possible heading 
    end_index = text_from_intro.lower().find("Background")  # like next tilte name
    if end_index != -1:
        text_from_intro = text_from_intro[:end_index]
    return text_from_intro
def process_pdfs_in_folder(pdf_folder):#whatever in folder it will be proccessd
    output_folder = "extracted_introductions" #results
    os.makedirs(output_folder, exist_ok=True)
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        try:
            intro_text = extract_introduction_from_pdf(pdf_path) #extract intro
            if intro_text:
                output_file = os.path.join(output_folder, f"{os.path.splitext(pdf_file)[0]}_introduction.txt") #save the extracted intro in per file .txt here
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(intro_text)
                print(f"Introduction extracted and saved for {pdf_file}")
            else:
                print(f"Introduction not found in {pdf_file}")
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")
#main
pdf_folder = 'pdf'  #raw pdf folder
process_pdfs_in_folder(pdf_folder)
