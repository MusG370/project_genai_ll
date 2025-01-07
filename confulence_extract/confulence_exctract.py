import requests
import os
import json
from bs4 import BeautifulSoup
from cred import CONFLUENCE_API_TOKEN,CONFLUENCE_USERNAME

# Step 1: Set up API credentials and base URL
BASE_URL = "https://altimetrik-team-xhojgpmb.atlassian.net/wiki/rest/api"
# USERNAME = os.getenv("CONFLUENCE_USERNAME")  # Set this as an environment variable
# API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")  # Set this as an environment variable

USERNAME=CONFLUENCE_USERNAME
API_TOKEN=CONFLUENCE_API_TOKEN

if not USERNAME or not API_TOKEN:
    print("Error: Missing Confluence credentials. Set CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN.")
    exit(1)

auth = (USERNAME, API_TOKEN)

# Step 2: Fetch all pages
def fetch_all_pages():
    url = f"{BASE_URL}/content"
    params = {
        "type": "page",
        "limit": 100,
        "expand": "ancestors"
    }
    response = requests.get(url, params=params, auth=auth)
    if response.status_code != 200:
        print(f"Failed to fetch pages: {response.status_code}, {response.text}")
        exit(1)
    return response.json()["results"]

# Step 3: Fetch content for a specific page by ID
def fetch_page_content(page_id):
    url = f"{BASE_URL}/content/{page_id}?expand=body.storage"
    response = requests.get(url, auth=auth)
    if response.status_code != 200:
        print(f"Failed to fetch content for page {page_id}: {response.status_code}, {response.text}")
        return None
    return response.json()

# Step 4: Extract data for all pages
def extract_pages_data():
    pages = fetch_all_pages()
    extracted_data = []
    for page in pages:
        page_id = page["id"]
        page_title = page["title"]
        page_content_response = fetch_page_content(page_id)
        if page_content_response:
            # Extract and clean the content
            raw_html = page_content_response["body"]["storage"]["value"]
            soup = BeautifulSoup(raw_html, "html.parser")
            clean_content = soup.prettify()

            # Add to extracted data
            extracted_data.append({
                "Page ID": page_id,
                "Page Title": page_title,
                "Page Content": clean_content
            })
    return extracted_data

# Step 5: Save extracted data to a file
def save_data_to_file(data, filename="confluence_pages_new.json"):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {filename}")

# Main execution
if __name__ == "__main__":
    data = extract_pages_data()
    save_data_to_file(data)
