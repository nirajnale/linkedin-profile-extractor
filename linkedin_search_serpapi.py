import requests
import json
import os
import time
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# 🔧 Generate linkedin_queries.json if missing
def generate_linkedin_queries():
    print("⚙️ Generating 'linkedin_queries.json' from companies_crawled.csv or companies_list.csv...")

    # Try 'companies_crawled.csv' first
    try:
        df = pd.read_csv("companies_crawled.csv")
        if "company_name" in df.columns:
            company_names = df["company_name"].dropna().unique()
        else:
            raise KeyError("Missing 'company_name' column")
    except:
        # Fallback to 'companies_list.csv'
        df = pd.read_csv("companies_list.csv")
        if "Company Name" in df.columns:
            company_names = df["Company Name"].dropna().unique()
        else:
            print("❌ Couldn't find valid company name column in fallback CSV.")
            return []

    roles = ["HR Manager", "HR", "Human Resources", "Recruiter", "Talent Acquisition"]

    queries = []
    for company in company_names:
        base_name = company.split("-")[0].strip()  # Remove trailing descriptions
        for role in roles:
            queries.append(f"{role} at {base_name}")

    with open("linkedin_queries.json", "w", encoding="utf-8") as f:
        json.dump(queries, f, indent=2)

    print(f"✅ Created 'linkedin_queries.json' with {len(queries)} queries.")
    return queries

# 🔍 Load or create LinkedIn queries
def read_queries(path="linkedin_queries.json"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return generate_linkedin_queries()

# 🔎 LinkedIn scraping via SerpAPI
def search_linkedin_profiles(query):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": f'site:linkedin.com/in "{query}"',
        "api_key": SERPAPI_KEY,
        "num": 5
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        results = response.json()
        profiles = []
        for result in results.get("organic_results", []):
            link = result.get("link", "")
            title = result.get("title", "")
            if "linkedin.com/in/" in link:
                profiles.append({
                    "query": query,
                    "title": title,
                    "url": link
                })
        return profiles
    else:
        print(f"❌ Error for query '{query}' | Status Code: {response.status_code}")
        return []

# 🚀 Main runner
if __name__ == "__main__":
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY is missing in .env file")
        exit()

    queries = read_queries()
    print(f"\n🔍 Running {len(queries)} LinkedIn searches using SerpAPI...\n")

    all_results = []
    for query in queries:
        print(f"🔎 Searching: {query}")
        profiles = search_linkedin_profiles(query)
        if profiles:
            all_results.extend(profiles)
            print(f"✅ Found {len(profiles)} profiles.")
        else:
            print("⚠️ No results found.")
        time.sleep(2)

    with open("linkedin_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✔ Done. Saved {len(all_results)} results to 'linkedin_results.json'.")
