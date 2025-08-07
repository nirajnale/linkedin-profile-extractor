import requests
import json
import os
import time
from dotenv import load_dotenv
import pandas as pd

# Load tokens
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
LINKEDIN_SESSION_COOKIE = os.getenv("LINKEDIN_SESSION_COOKIE")
ACTOR_ID = "2SyF0bVxmgGr8IVCZ"  # Apify LinkedIn Profile Scraper

def normalize_linkedin_url(url):
    if not url or "linkedin.com/in/" not in url:
        return None
    url = url.split("?")[0]
    url = url.replace("mx.linkedin.com", "www.linkedin.com")
    if not url.startswith("https://"):
        url = "https://" + url
    return url.strip()

def run_profile_scraper(profile_urls):
    headers = {
        "Authorization": f"Bearer {APIFY_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "profileUrls": profile_urls,
        "includeSkills": True,
        "includeRecommendations": True,
        "sessionCookie": LINKEDIN_SESSION_COOKIE
    }

    print("\n🔄 Payload being sent to Apify:\n", json.dumps(payload, indent=2))

    # Step 1: Trigger actor run
    run_url = f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={APIFY_TOKEN}"
    run_response = requests.post(run_url, headers=headers, json=payload)

    if run_response.status_code != 201:
        print(f"❌ Failed to start actor. Status: {run_response.status_code}")
        print(run_response.text)
        return []

    run_data = run_response.json()
    run_id = run_data.get("data", {}).get("id")

    print(f"🟢 Actor started. Run ID: {run_id}. Waiting for it to finish...")

    # Step 2: Poll for completion
    while True:
        status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
        status_response = requests.get(status_url)
        status = status_response.json().get("data", {}).get("status")
        if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            print(f"🔁 Run finished with status: {status}")
            break
        time.sleep(5)

    if status != "SUCCEEDED":
        return []

    # Step 3: Fetch dataset results
    dataset_id = status_response.json().get("data", {}).get("defaultDatasetId")
    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"
    data_response = requests.get(dataset_url)

    results = []
    if data_response.status_code == 200:
        try:
            data = data_response.json()
            for item in data:
                results.append({
                    "fullName": item.get("fullName", ""),
                    "headline": item.get("headline", ""),
                    "url": item.get("url", ""),
                    "location": item.get("location", ""),
                    "currentCompany": item.get("company", ""),
                    "skills": item.get("skills", [])
                })
        except Exception as e:
            print(f"⚠️ Error parsing data: {e}")
    else:
        print(f"❌ Failed to fetch dataset. Status: {data_response.status_code}")
        print(data_response.text)

    return results

if __name__ == "__main__":
    try:
        with open("linkedin_results.json", "r", encoding="utf-8") as f:
            search_results = json.load(f)

        profile_urls = []
        for item in search_results:
            url = normalize_linkedin_url(item.get("url", ""))
            if url:
                profile_urls.append(url)

        if not profile_urls:
            print("⚠️ No valid LinkedIn profile URLs found in 'linkedin_results.json'.")
        else:
            print(f"\n🔍 Scraping {len(profile_urls)} LinkedIn profiles in batches...\n")
            all_results = []

            for i in range(0, len(profile_urls), 3):
                batch = profile_urls[i:i+3]
                print(f"\n📦 Scraping batch {i//3 + 1}: {len(batch)} profiles")
                batch_results = run_profile_scraper(batch)
                all_results.extend(batch_results)
                time.sleep(10)  # ⏱ Wait 10s to avoid rate limiting

            # Save the combined results
            with open("linkedin_profiles_scraped.json", "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=2)

            print(f"\n✅ Done. Scraped {len(all_results)} profiles to 'linkedin_profiles_scraped.json'.\n")

    except FileNotFoundError:
        print("❌ File 'linkedin_results.json' not found. Please run the LinkedIn search step first.")
