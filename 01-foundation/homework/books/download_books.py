import pandas as pd
from markitdown.pdf import download_pdf
from urllib.parse import urlparse
import os

# Path to the CSV file
csv_path = "books.csv"
# Output directory for PDFs
output_dir = "pdfs"
os.makedirs(output_dir, exist_ok=True)

# Read the CSV
books = pd.read_csv(csv_path)

for url in books['pdf_url']:
    if pd.isna(url):
        continue
    # Extract the filename from the URL
    filename = os.path.basename(urlparse(url).path)
    output_path = os.path.join(output_dir, filename)
    print(f"Downloading {url} -> {output_path}")
    download_pdf(url, output_path)
print("All PDFs downloaded.")
