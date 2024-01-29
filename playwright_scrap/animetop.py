from fastapi import FastAPI
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json

app = FastAPI()

def get_html_content(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html_content = page.content()
        browser.close()
    return html_content

@app.get("/topanime")
def scrape_myanimelist():
    url = 'https://myanimelist.net/topanime.php'
    html_content = get_html_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')

    rows = soup.select('div.pb12 > table > tbody > tr')

    for i, row in enumerate(rows, start=1):
        ranking = row.select_one('td.rank.ac > span')
        title = row.select_one('td.title.al.va-t.word-break > div > div.di-ib.clearfix > h3')
        score = row.select_one('td.score.ac.fs14 > div > span')

        if ranking and title and score:
            result = {
                "ranking": ranking.text.strip(),
                "title": title.text.strip(),
                "score": score.text.strip()
            }

            # Write result to a separate JSON file for each row
            with open(f'topanime_data_{i}.json', 'w') as json_file:
                json.dump(result, json_file, indent=2)

    return {"message": "Scraping completed. Check the generated JSON files."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)