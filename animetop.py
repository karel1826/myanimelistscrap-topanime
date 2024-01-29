from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import json

app = FastAPI()

def get_html_content(url):
    driver = webdriver.Chrome()
    driver.get(url)
    html_content = driver.page_source
    driver.quit()
    return html_content

@app.get("/anime-list")
async def get_anime_list():
    url = 'https://myanimelist.net/topanime.php'
    html_content = get_html_content(url)
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.select('tr')

    anime_list = []
    for index, row in enumerate(rows):
        ranking = row.select_one('td.rank > span')
        title = row.select_one('td.title > div > div > h3')
        score = row.select_one('td.score > div > span')

        if ranking and title and score:
            anime_data = {
                "ranking": ranking.text,
                "title": title.text,
                "score": score.text
            }

        
            json_file_path = f"anime_data_{index + 1}.json"
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(anime_data, json_file, ensure_ascii=False, indent=2)

            anime_list.append(anime_data)
        else:
            print(f"Error in processing data for row {index + 1}")

    if anime_list:
        return JSONResponse(content={"message": "Scrap data has been successfully created"})
    else:
        raise HTTPException(status_code=500, detail="Error in processing data. Scrap data creation failed.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)