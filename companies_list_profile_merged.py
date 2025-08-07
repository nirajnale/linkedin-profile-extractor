import pandas as pd
import json
from fuzzywuzzy import process, fuzz

# ---------- STEP 1: Load companies ----------
companies_df = pd.read_csv("companies_list.csv")
companies_df["Company Name"] = (
    companies_df["Company Name"]
    .astype(str)
    .str.strip()
    .str.lower()
    .str.split("|").str[0]
    .str.split("-").str[0]
    .str.strip()
)

print("\n📄 Sample from companies_df:")
print(companies_df[["Company Name", "Company Website"]].head(10))

# ---------- STEP 2: Load LinkedIn profiles ----------
with open("linkedin_profiles_scraped.json", "r", encoding="utf-8") as f:
    profiles_data = json.load(f)

profiles_df = pd.DataFrame(profiles_data)

# Extract company from skills/headline if currentCompany is missing
def extract_company(profile):
    if profile.get("currentCompany"):
        return profile["currentCompany"]
    skills = profile.get("skills", [])
    for skill in skills:
        for sub in skill.get("subComponents", []):
            for desc in sub.get("description", []):
                text = desc.get("text", "")
                if " at " in text.lower():
                    return text.split(" at ")[-1]
    headline = profile.get("headline", "")
    if " at " in headline.lower():
        return headline.split(" at ")[-1]
    return ""

profiles_df["clean_company"] = profiles_df.apply(extract_company, axis=1)
profiles_df["clean_company"] = profiles_df["clean_company"].astype(str).str.lower().str.strip()
profiles_df = profiles_df[profiles_df["clean_company"] != ""]

# ---------- STEP 3: Match LinkedIn profiles to companies ----------
matched_companies = []
scores = []

for company in profiles_df["clean_company"]:
    result = process.extractOne(company, companies_df["Company Name"], scorer=fuzz.partial_ratio, score_cutoff=80)
    if result is not None and isinstance(result, tuple):
        match = result[0]
        score = result[1]
        matched_companies.append(match)
        scores.append(score)
    else:
        matched_companies.append(None)
        scores.append(0)

profiles_df["Matched Company Name"] = matched_companies
profiles_df["Match Score"] = scores

merged_df = pd.merge(
    profiles_df,
    companies_df,
    how="left",
    left_on="Matched Company Name",
    right_on="Company Name"
)

final_df = merged_df[[
    "Company Name",
    "Company Website",
    "fullName",
    "url",
    "headline",
    "location"
]]

final_df.columns = [
    "Company Name",
    "Company Website",
    "HR Manager Name",
    "HR Manager LinkedIn Profile URL",
    "Designation",
    "Location"
]

# ---------- STEP 4: Enrich LinkedIn URLs from linkedin_results.json ----------
try:
    with open("linkedin_results.json", "r", encoding="utf-8") as f:
        linked_results = json.load(f)

    print("\n🔗 Loaded linkedin_results.json with", len(linked_results), "records.")

    # Create title-to-URL mapping
    title_url_map = {}
    for item in linked_results:
        title = item.get("title", "").strip().lower()
        url = item.get("url", "").strip()
        if " - " in title:
            extracted_title = title.split(" - ", 1)[1]  # Skip name
        else:
            extracted_title = title
        if extracted_title and url:
            title_url_map[extracted_title.strip()] = url

    # Create match key for each row in final_df
    final_df["Designation"] = final_df["Designation"].fillna("").astype(str).str.strip().str.lower()
    final_df["Company Name"] = final_df["Company Name"].fillna("").astype(str).str.strip().str.lower()
    final_df["match_key"] = final_df["Designation"] + " at " + final_df["Company Name"]

    def find_url(match_key):
        for title, url in title_url_map.items():
            if fuzz.partial_ratio(match_key, title) >= 85:
                return url
        return None

    final_df["HR Manager LinkedIn Profile URL"] = final_df["HR Manager LinkedIn Profile URL"].fillna("")
    final_df["HR Manager LinkedIn Profile URL"] = final_df.apply(
        lambda row: row["HR Manager LinkedIn Profile URL"] or find_url(row["match_key"]),
        axis=1
    )

    final_df.drop(columns=["match_key"], inplace=True)
    print("✅ Enriched LinkedIn URLs using linkedin_results.json.")

except FileNotFoundError:
    print("⚠️ linkedin_results.json not found. Skipping enrichment.")

# ---------- STEP 5: Save result ----------
final_df.to_csv("final_linkedin_profiles.csv", index=False)
print("✅ Final CSV exported as final_linkedin_profiles.csv")
