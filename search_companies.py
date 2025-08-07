import os
import requests
import pandas as pd
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load SerpAPI Key
load_dotenv()
api_key = os.getenv("SERPAPI_KEY")  # Make sure you add this key in .env

if not api_key:
    print("❌ SERPAPI_KEY not found. Add it to your .env file.")
    exit()

print("🔑 Using SerpAPI Key:", api_key)

# Query list
queries = [
    "Top construction companies in Mexico",
    "Civil engineering companies Mexico",
    "Real estate builders Mexico",
    "Infrastructure firms in Mexico",
    "Best contractors Mexico",
    "Mexican construction firms list"
]

EXCLUDE_DOMAINS = [
    "wikipedia.org", "statista.com", "glassdoor.com", "dnb.com",
    "ensun.io", "explore", "youtube.com", "facebook.com", "instagram.com",
    "bloomberg.com", "crunchbase.com", "investing.com", "zoominfo.com",
    "lusha.com", "mexicotoprated.com", "aeroleads.com", "clutch.co",
    "yelp.com", "houzz.com", "f6s.com", "mexlife.com", "manifest.com",
    "themanifest.com", "caribeluxuryhomes.com", "legal500.com",
    "constructionreviewonline.com", "bolddata.nl", "angie.com",
    "angi.com", "taomexico.com", "sayulitalife.com", "d7leadfinder.com",
    "rentechdigital.com", "mexicoliving.com"
]

def is_valid_company_url(url):
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()

        # Exclude known non-company domains
        if any(excl in domain for excl in EXCLUDE_DOMAINS):
            return False
        
        # Reject URLs that are just directories/articles
        bad_keywords = ['news', 'top', 'review', 'article', 'list', 'blog', 'press']
        if any(k in path for k in bad_keywords):
            return False

        # Reject pages deep into path (e.g., /blog/2023/top-companies)
        if path.count("/") > 2:
            return False

        return True
    except:
        return False
companies = []

for query in queries:
    print(f"\n🔍 Searching: {query}")
    params = {
        "api_key": api_key,
        "engine": "google",
        "q": query,
        "gl": "mx",  # Mexico local
        "hl": "en",
        "num": 20
    }
    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()

    for result in data.get("organic_results", []):
        title = result.get("title")
        link = result.get("link")
        if is_valid_company_url(link):
            companies.append({
                "Company Name": title,
                "Company Website": link
            })

# Save results
if companies:
    df = pd.DataFrame(companies).drop_duplicates(subset="Company Website")
    df.to_csv("companies_list.csv", index=False)
    print(f"\n✅ Saved {len(df)} unique companies to 'companies_list.csv'")
else:
    print("⚠️ No companies extracted.")
