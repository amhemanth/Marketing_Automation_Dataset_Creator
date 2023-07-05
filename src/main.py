import requests
from bs4 import BeautifulSoup
import json
from DataSetGenerator import GetDataSet
from tqdm import tqdm
from colorama import Fore, Style
from urllib.parse import urlparse
from urllib.parse import urljoin

def get_urls_from_blog(blog_urls):
    # Send a GET request to the website
    response = requests.get(blog_urls)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all anchor tags in the HTML
        anchor_tags = soup.find_all('a')

        # Extract the URLs from the anchor tags
        urls = [tag.get('href') for tag in anchor_tags]

        # Filter out None and empty URLs
        urls = [url for url in urls if url is not None and url != '' and url.endswith('.html')]

        # Remove URLs containing specific terms
        urls = [url for url in urls if not any(term in url.lower() for term in ["terms-of-condition", "cookie-policy", "privacy-statement", "safe-harbor-provision", "terms-of-use"])]

        # Get the domain URL
        domain_url = urlparse(blog_urls).netloc

        # Filter out URLs that do not have the domain URL
        urls = [url for url in urls if domain_url in url]

        # Get unique URLs
        urls = list(set(urls))

        return urls
    else:
        print(f"Failed to retrieve URLs from {blog_urls}")
        return []

def prepare_dataset(urls):
    dataset = []
    for url in tqdm(urls, desc="Processing items", unit="item", bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Style.RESET_ALL)):
        # Fetch additional information for each URL
        # Create a data dictionary for the URL
        data = GetDataSet(url)

        # Add the data to the dataset list
        dataset.append(data)

    return dataset

def download_dataset(dataset, file_path):
    with open(file_path, 'w') as json_file:
        json.dump(dataset, json_file, indent=4)
    print(f"Dataset downloaded to {file_path}")

def scrape_website(start_year, end_year):
    base_url = 'https://www.infosys.com/newsroom/press-releases.html'  # Replace with the base URL of the website
    current_year = start_year
    unique_urls = []

    with tqdm(total=end_year - start_year + 1) as pbar:
        while current_year <= end_year:
            url = f'{base_url}?year={current_year}'  # Modify the URL to include the current year parameter

            # Send a GET request to the URL
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the links from the current page
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and href.endswith('.html') and 'press-releases' in href:
                    full_url = urljoin(base_url, href)
                    unique_urls.append(full_url)

            # Find and click on the "Show More" button
            show_more_button = soup.find('button', text='Show More')
            if show_more_button and show_more_button.get('href'):
                # Simulate clicking the "Show More" button
                next_url = urljoin(base_url, show_more_button.get('href'))
                response = requests.get(next_url)
                soup = BeautifulSoup(response.content, 'html.parser')
            else:
                current_year += 1

            pbar.update(1)  # Update the progress bar

    # Remove duplicates and return the unique URLs
    unique_urls = list(set(unique_urls))
    return unique_urls

# Initialize colorama
Fore.BLUE, Fore.GREEN, Fore.YELLOW, Fore.RED, Style.RESET_ALL

# Specify the website URL
website_urls = ["https://blogs.infosys.com/all-blogs", 
                "https://blogs.infosys.com/infosys-cobalt/",
                "https://blogs.infosys.com/infosys-cobalt/cloud-analytics",
                "https://blogs.infosys.com/emerging-technology-solutions/artificial-intelligence",
                "https://blogs.infosys.com/infosys-cobalt/cloud-applications",
                "https://blogs.infosys.com/infosys-cobalt/cloud-platforms",
                "https://blogs.infosys.com/infosys-cobalt/cyber-security",
                "https://blogs.infosys.com/infosys-cobalt/digital-process-automation",
                "https://blogs.infosys.com/infosys-cobalt/digital-supply-chain",
                "https://blogs.infosys.com/infosys-cobalt/private-hybrid-cloud",
                "https://blogs.infosys.com/infosys-cobalt/public-cloud",
                "https://blogs.infosys.com/infosys-cobalt/salesforce",
                "https://blogs.infosys.com/emerging-technology-solutions/artificial-intelligence",
                "https://blogs.infosys.com/emerging-technology-solutions/datanext",
                "https://blogs.infosys.com/emerging-technology-solutions/privacynext",
                "https://blogs.infosys.com/quality-engineering/cloud-testing",
                "https://blogs.infosys.com/healthcare/",
                "https://blogs.infosys.com/life-sciences/",
                "https://blogs.infosys.com/engineering-services/",
                "https://blogs.infosys.com/sap/",
                "https://blogs.infosys.com/application-modernization/",
                "https://blogs.infosys.com/nextgen-devops/"
            ]

# Get the list of URLs from the website
urls = []
for website_url in website_urls: 
    urls += get_urls_from_blog(website_url)

# Usage
start_year = 2000  # Starting year
end_year = 2023  # Ending year
result = scrape_website(start_year, end_year)
urls += result

# Prepare the dataset using the URLs
dataset = prepare_dataset(urls)

# Specify the file path for the dataset JSON file
file_path = "../data/dataset.json"

# Download the dataset in JSON format
download_dataset(dataset, file_path)
