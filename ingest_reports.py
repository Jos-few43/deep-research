import os
import json
import requests
import re

MEILI_URL = "http://127.0.0.1:7700"
MEILI_KEY = "antigravity-deep-research"
REPORTS_DIR = "memory/research/reports"
INDEX_NAME = "reports"

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9-_]', '_', text.lower())

def ingest():
    headers = {
        "Authorization": f"Bearer {MEILI_KEY}",
        "Content-Type": "application/json"
    }

    # Ensure index exists and primary key is set to 'id'
    print(f"Checking index: {INDEX_NAME}...")
    
    documents = []
    
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith(".md"):
            path = os.path.join(REPORTS_DIR, filename)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title (first H1)
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else filename
            
            doc_id = slugify(filename.replace(".md", ""))
            
            documents.append({
                "id": doc_id,
                "title": title,
                "filename": filename,
                "content": content,
                "type": "report"
            })
            print(f"Prepared: {filename}")

    if not documents:
        print("No documents found.")
        return

    # Add documents to Meilisearch
    url = f"{MEILI_URL}/indexes/{INDEX_NAME}/documents"
    response = requests.post(url, headers=headers, json=documents)
    
    if response.status_code in [200, 201, 202]:
        print(f"Successfully sent {len(documents)} documents to Meilisearch.")
        print(f"Task ID: {response.json().get('taskUid')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    ingest()
