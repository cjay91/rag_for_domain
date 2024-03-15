import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
import os

def get_sites(url):
    # url = 'https://www.dilmahtea.com/'
    reqs = requests.get(url)
    soup = BeautifulSoup(reqs.text, 'html.parser')

    base_url = url.rstrip('/')  # Remove trailing slash if exists

    urls = []
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.startswith('/'):
            full_url = urljoin(base_url, href)
            urls.append(full_url)

    return urls

def generate_dataset(urls: list):
    data = []
    i=0
    for url in tqdm(urls, desc="URLs"):
        if(i<=5):
            try:
                # Send HTTP request to the URL
                response = requests.get(url)
                response.raise_for_status()  # Check for successful response
                # Parse HTML content
                soup = BeautifulSoup(response.content, "html.parser")
                
                paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
                content = "\n".join(paragraphs)
                d = {
                    "url": url,
                    "body": content,
                }
                data.append(d)
            except requests.exceptions.HTTPError as errh:
                print(f"HTTP Error: {errh}")
            except requests.exceptions.ConnectionError as errc:
                print(f"Error Connecting: {errc}")
            except requests.exceptions.Timeout as errt:
                print(f"Timeout Error: {errt}")
            except requests.RequestException as err:
                print(f"Error during requests to {url}: {str(err)}")
            i = i+1
    return data

def scrape(domain) -> None:

    list_of_websites = get_sites(domain)
    data = generate_dataset(list_of_websites)

    for paragraph in data:
        url = paragraph["url"]
        body = paragraph["body"]

        # Create directory for the website if it doesn't exist
        website_dir = os.path.join('docs', domain.lstrip('https://').rstrip('/').replace('/', '_'))
        os.makedirs(website_dir, exist_ok=True)

        # Create a file with the URL as its name
        filename = f"{url.replace('/', '_').replace(':', '_')}.txt"
        file_path = os.path.join(website_dir, filename)

        # Check if the file exists, if not, create it
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                file.write(body)

# scrape("https://www.dilmahtea.com/")