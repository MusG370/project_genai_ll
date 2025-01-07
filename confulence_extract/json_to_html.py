import json
from bs4 import BeautifulSoup

# Load the JSON file containing all pages
file_path = "/Users/muskaangupta/Documents/CONFULENCE_EXTRACT/confluence_pages_new.json"
with open(file_path, "r") as file:
    pages_data = json.load(file)

# Function to dynamically extract structured data from page content
def extract_structured_data(page_data):
    structured_data = {}

    # Extract basic fields: Page ID and Title
    structured_data["Page ID"] = page_data.get("Page ID", "")
    structured_data["Page Title"] = page_data.get("Page Title", "")

    # Parse the Page Content (HTML) using BeautifulSoup
    page_content = page_data.get("Page Content", "")
    soup = BeautifulSoup(page_content, "html.parser")

    # Extract all sections with <h2> or similar tags
    sections = soup.find_all(['h2', 'h3', 'h4', 'h5'])
    
    for section in sections:
        section_title = section.get_text(strip=True)
        
        # Get content associated with each section
        next_sibling = section.find_next_sibling()
        section_content = []

        # Collect content under the section until another heading is found
        while next_sibling and next_sibling.name not in ['h2', 'h3', 'h4', 'h5']:
            if next_sibling.name == 'p':
                section_content.append(next_sibling.get_text(strip=True))
            elif next_sibling.name == 'ul':
                # For unordered lists, extract list items
                items = [li.get_text(strip=True) for li in next_sibling.find_all('li')]
                section_content.extend(items)
            elif next_sibling.name == 'table':
                # For tables, extract rows
                rows = []
                for row in next_sibling.find_all('tr'):
                    cols = [col.get_text(strip=True) for col in row.find_all('td')]
                    rows.append(cols)
                section_content.append(rows)
            next_sibling = next_sibling.find_next_sibling()

        # Store the extracted section content in structured_data
        structured_data[section_title] = section_content

    return structured_data

# Process all pages and extract structured data
all_structured_data = []
for page in pages_data:
    structured_page_data = extract_structured_data(page)
    all_structured_data.append(structured_page_data)

# Save the structured data to a new JSON file
output_path = "/Users/muskaangupta/Documents/CONFULENCE_EXTRACT/structured_pages_data.json"
with open(output_path, "w") as output_file:
    json.dump(all_structured_data, output_file, indent=2)

print(f"Structured data has been saved to: {output_path}")
