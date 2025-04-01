import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

BASE_URL = "https://toscan.net" # Remplacer par l'URL de votre site

# Max number of pages to crawl
MAX_PAGES = 100

def get_internal_links(base_url):
    visited = set()
    to_visit = {base_url}
    domain = urlparse(base_url).netloc
    internal_links = set()

    while to_visit and len(visited) < MAX_PAGES:
        current_url = to_visit.pop()
        if current_url in visited:
            continue
        visited.add(current_url)
        try:
            resp = requests.get(current_url, timeout=10)
            if not resp.headers.get("Content-Type", "").startswith("text/html"):
                continue
            soup = BeautifulSoup(resp.text, "html.parser")
            for a_tag in soup.find_all("a", href=True):
                href = a_tag['href']
                full_url = urljoin(current_url, href)
                parsed = urlparse(full_url)
                if parsed.netloc == domain and full_url not in visited:
                    to_visit.add(full_url)
                    internal_links.add(full_url)
        except Exception:
            continue

    return sorted(internal_links)

def check_endpoints(endpoints):
    results = []
    for url in endpoints:
        entry = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat()
        }
        try:
            response = requests.get(url, timeout=10)
            entry["status_code"] = response.status_code
        except requests.RequestException as e:
            entry["status_code"] = "ERROR"
            entry["error"] = str(e)
        results.append(entry)
    return results

def write_report(results, report_file):
    total = len(results)
    failures = [r for r in results if r.get("status_code") in [400, 404, 500, "ERROR"]]
    with open(report_file, mode="w", encoding="utf-8") as file:
        file.write("Endpoint Check Report\n")
        file.write(f"Generated on: {datetime.utcnow().isoformat()}\n")
        file.write(f"Total URLs checked: {total}\n")
        file.write(f"Total failures: {len(failures)}\n")
        file.write("="*60 + "\n\n")
        for result in results:
            file.write(f"URL : {result['url']}\n")
            file.write(f"Status Code : {result['status_code']}\n")
            file.write(f"Checked at : {result['timestamp']}\n")
            if 'error' in result:
                file.write(f"Error: {result['error']}\n")
            file.write("-"*40 + "\n")

def main():
    print(f"Crawling site: {BASE_URL}")
    links = get_internal_links(BASE_URL)
    print(f"{len(links)} endpoints found.")
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    report_file = f"endpoint_report_{date_str}.txt"
    results = check_endpoints(links)
    write_report(results, report_file)
    print(f"Report written to {report_file}")

if __name__ == "__main__":
    main()
