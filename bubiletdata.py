from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import uuid

class BuBiletScraper:
    def __init__(self, file_path):
        self.file_path = file_path
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("window-size=1920x1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-networking")

        self.service = Service("chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.set_page_load_timeout(30)

    def fetch_links(self):
        links = []
        self.driver.get('https://www.bubilet.com.tr/ankara')
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        findiv = soup.find_all("a", class_="group block")
        for div in findiv:
            href = div.get("href")
            if href:
                full_link = "https://www.bubilet.com.tr" + href
                links.append(full_link)
        return links

    def scrape_data(self, links):
        all_data = []
        counter = 0
        for link in links:
            counter += 1
            time.sleep(0.1)
            try:
                self.driver.get(link)
                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                time.sleep(0.2)
                name = soup.find("h1").text.strip() if soup.find("h1") else ""
                price_tag = soup.find("span", class_="text-lg font-semibold text-emerald-600")
                price = price_tag.text.strip() if price_tag else ""
                id = uuid.uuid4()
                info_divs = soup.find_all("div", class_="flex items-center space-x-1")
                spanarray = [span.text.strip() for div in info_divs if (span := div.find("span"))]

                if len(spanarray) >= 3:
                    new_data = {
                        'Day': spanarray[0],
                        'Price': price,
                        'Hour': spanarray[1],
                        'Name': name,
                        'Map': spanarray[2],
                        'link': link,
                        'id' : id,
                        'website': "Bubilet"

                    }
                    all_data.append(new_data)
                    print(f"Kaydedilen: {name} | {spanarray[0]} {spanarray[1]} | {spanarray[2]} | {price}")
                else:
                    continue
                if counter >= 40:
                    break
            except Exception as e:
                print(f"Error processing {link}: {e}")
                continue

        df = pd.DataFrame(all_data, columns=["Day", "Price", "Hour", "Name", "Map", "link","id", "website"])
        df.to_csv(self.file_path, mode='w', header=True, index=False, encoding='utf-8-sig')
        df.to_excel(self.file_path.replace('.csv', '.xlsx'), index=False, engine='openpyxl')

    def close(self):
        self.driver.quit()
