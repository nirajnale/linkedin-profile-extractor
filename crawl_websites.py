import requests
from bs4 import BeautifulSoup
import pandas as pd

def extract_company_name(soup):
    title = soup.title.string.strip() if soup.title else ""
    meta_title = soup.find("meta", attrs={"property": "og:site_name"}) or \
                 soup.find("meta", attrs={"name": "og:title"}) or \
                 soup.find("meta", attrs={"name": "title"})
    if meta_title and meta_title.get("content"):
        return meta_title["content"].strip()
    return title or "N/A"

def extract_linkedin(soup):
    for a in soup.find_all("a", href=True):
        if "linkedin.com" in a["href"]:
            return a["href"]
    return "Not Found"

def extract_contact_page(soup, base_url):
    for a in soup.find_all("a", href=True):
        text = (a.text or "").lower()
        href = a["href"].lower()
        if "contact" in href or "contact" in text or "get in touch" in text:
            link = a["href"]
            if link.startswith("http"):
                return link
            elif link.startswith("/"):
                return base_url.rstrip("/") + link
    return "Not Found"

def crawl_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        company_name = extract_company_name(soup)
        linkedin_url = extract_linkedin(soup)
        contact_page_url = extract_contact_page(soup, url)

        return {
            "Company Website": url,
            "Company Name": company_name,
            "Company LinkedIn Page URL": linkedin_url,
            "Contact Page": contact_page_url,
            "Status": "Success"
        }
    except Exception as e:
        return {
            "Company Website": url,
            "Company Name": "",
            "Company LinkedIn Page URL": "",
            "Contact Page": "",
            "Status": f"Failed: {str(e)}"
        }

def main():
    try:
        df = pd.read_csv("companies_list.csv")
        if "Company Website" not in df.columns:
            print("❌ CSV file must contain a 'Company Website' column.")
            return
        urls = df["Company Website"].dropna().tolist()
    except FileNotFoundError:
        print("❌ File 'companies_list.csv' not found.")
        return
    
    results = []

    print("\n🔎 Starting crawl...\n")
    for url in urls:
        print(f"Crawling: {url}")
        result = crawl_page(url)
        print(f"[{result['Status']}] {url}")
        results.append(result)

    pd.DataFrame(results).to_csv("companies_crawled.csv", index=False)
    print("\n✅ Crawl completed. Results saved to 'companies_crawled.csv'")

if __name__== "__main__":
    main()
