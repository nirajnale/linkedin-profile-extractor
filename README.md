# 🕵️‍♂️ LinkedIn Scraper for HR Managers of Construction Companies in Mexico

This project automates the end-to-end process of discovering construction companies in Mexico, crawling their websites, extracting HR Manager LinkedIn profiles, and enriching the data using AI tools.

---

## 📌 Objective

To develop a Python-based solution that:
- Discovers construction companies in Mexico.
- Extracts company and LinkedIn data using search engines and scraping tools.
- Identifies HR managers from LinkedIn.
- Enriches the final data file with descriptions using AI (LLM) tools.

---

## 📁 Project Structure

```
.
├── search_companies.py                # Step 1: Discover companies via SerpAPI
├── crawl_websites.py                 # Step 2: Crawl websites for company details
├── linkedin_search_serpapi.py       # Step 3: Search LinkedIn profiles using Google
├── apify_runner.py                  # Step 4: Extract detailed profile data from LinkedIn using Apify
├── companies_list_profile_merged.py # Step 5: Merge company + profile data
├── summary_gemini_api.py            # Step 6: Optional AI summarization using Gemini
├── final_linkedin_profiles_with_descriptions.csv # ✅ Final Output
├── README.md
└── .env                              # Contains API keys (not shared publicly)
```

---

## 🔧 Tools & Technologies Used

| Tool/API           | Purpose                                           |
|--------------------|---------------------------------------------------|
| Python             | Core programming language                         |
| SerpAPI            | Google search engine scraping                     |
| Apify              | LinkedIn profile scraper                          |
| Gemini API (Google)| LLM-based company description generator (attempted) |
| OpenAI API         | Tried for enrichment, but requires payment        |
| BeautifulSoup      | HTML parsing and web crawling                     |
| Pandas             | Data handling and CSV processing                  |
| FuzzyWuzzy         | Fuzzy matching of company names                   |

---

## 🚀 Execution Workflow

### ✅ Step 1: Discover Companies

Script: `search_companies.py`  
- Uses **SerpAPI** to search for queries like “Top construction companies in Mexico”.
- Filters valid URLs.
- Saves to `companies_list.csv`.

### ✅ Step 2: Crawl Company Websites

Script: `crawl_websites.py`  
- Loads websites from CSV.
- Crawls and extracts:
  - Company Name
  - Company LinkedIn URL (if any)
  - Contact Page URL

### ✅ Step 3: Search LinkedIn Profiles

Script: `linkedin_search_serpapi.py`  
- Builds queries like “HR at {Company Name}”.
- Uses Google + SerpAPI to find LinkedIn profile URLs.
- Saves to `linkedin_results.json`.

### ✅ Step 4: Scrape LinkedIn Profiles

Script: `apify_runner.py`  
- Takes LinkedIn URLs.
- Uses **Apify** actor to extract:
  - Name, headline, company, skills, location, etc.
- Saves to `linkedin_profiles_scraped.json`.

### ✅ Step 5: Merge & Match Data

Script: `companies_list_profile_merged.py`  
- Cleans company names.
- Matches scraped profiles to companies using fuzzy logic.
- Joins data and prepares `final_linkedin_profiles.csv`.

### ✅ Step 6: AI Summarization (Optional)

Script: `summary_gemini_api.py`  
- Attempts to use **Gemini API** for writing a 2-line company description.
- Gemini API was **successfully integrated**, but **rate-limited** due to **free tier restrictions**.
- OpenAI API was **tested**, but **disabled due to pricing**.

---

## 📊 Final Output

The final CSV file: `final_linkedin_profiles_with_descriptions.csv` contains:

| Column                          | Description                          |
|---------------------------------|--------------------------------------|
| Company Name                    | Official Company Name                |
| Company Website                 | Website URL                          |
| LinkedIn Page URL               | Company LinkedIn page                |
| HR Manager Name                 | Person name                          |
| HR Manager LinkedIn Profile URL | Personal profile                     |
| Designation                     | Title (e.g., HR Manager)             |
| Location                        | If available                         |
| Company Description             | AI-generated summary (optional)      |

---

## 🔐 Environment Variables (.env)

| Variable Name            | Description                             |
|--------------------------|-----------------------------------------|
| `SERPAPI_KEY`            | API key for Google Search (SerpAPI)     |
| `APIFY_TOKEN`            | API key for Apify LinkedIn scraper      |
| `LINKEDIN_SESSION_COOKIE`| Your LinkedIn session cookie            |
| `GEMINI_API_KEY`         | Google Gemini LLM API key               |

> ⚠️ Ensure `.env` is present and never commit it to public repositories.

---

## 📦 Installation

```bash
git clone https://github.com/your-username/linkedin-profile-extractor.git
cd linkedin-profile-extractor
pip install -r requirements.txt
```

Ensure `.env` is configured with required API keys.

---

## 📅 Demo & Notes

The script was developed as a complete automated pipeline. Gemini/OpenAI LLMs were explored for enrichment, but due to API limits and billing issues, AI summaries are optional.

---

## 📞 Contact

Prepared by: **Niraj Nale**  
Submission for: *Web Crawling & LinkedIn Extraction Task*  

---
