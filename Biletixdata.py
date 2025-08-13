from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
import os
import time
import uuid
import requests

class BiletixScraper:
    def __init__(self, file_path):
        self.file_path = file_path

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("window-size=1920x1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--enable-unsafe-swiftshader")
        self.service = Service("chromedriver.exe")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.set_page_load_timeout(15)

    def get_links(self):
        url = "https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=-1&city_sb=Ankara#!city_sb:Ankara"
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading initial page: {e}")
            return []

        wait = WebDriverWait(self.driver, 15)
        while True:
            try:
                daha_fazla_btn = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "search_load_more")))
                self.driver.execute_script("arguments[0].click();", daha_fazla_btn)
                time.sleep(0.2)
            except:
                break

        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        etkinlikler = soup.find_all("a", class_="ln1 searchResultEventName")

        biletixlink = "https://www.biletix.com"
        links = []

        for etkinlik in etkinlikler:
            href = etkinlik.get("href")
            if href:
                full_url = biletixlink + href
                links.append(full_url)

        if links:
            links.pop(0) 
        return links


import os
import time
import uuid
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BiletixScraper:
    def __init__(self, file_path):
        self.file_path = file_path

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("user-agent=Mozilla/5.0")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.driver.set_page_load_timeout(15)

    def get_links(self):
        url = "https://www.biletix.com/search/TURKIYE/tr?category_sb=-1&date_sb=-1&city_sb=Ankara#!city_sb:Ankara"
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Error loading initial page: {e}")
            return []

        wait = WebDriverWait(self.driver, 15)
        while True:
            try:
                daha_fazla_btn = wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "search_load_more"))
                )
                self.driver.execute_script("arguments[0].click();", daha_fazla_btn)
                time.sleep(0.3)
            except:
                break

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        etkinlikler = soup.find_all("a", class_="ln1 searchResultEventName")

        links = []
        for etkinlik in etkinlikler:
            href = etkinlik.get("href")
            if href:
                links.append("https://www.biletix.com" + href)

        if links:
            links.pop(0)
        return links

    def scrape_data(self, links, image_folder=r"C:\Users\Kayra\Desktop\Napak\Photos"):
        all_data = []
        os.makedirs(image_folder, exist_ok=True)

        counter = 0
        bannedplaces = [...]  # senin liste

        for link in links:
            try:
                self.driver.get(link)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "performance-listing"))
                )

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                h1 = soup.find("h1").text if soup.find("h1") else ""
                if h1 in bannedplaces:
                    continue
                org_id = uuid.uuid4()
                image_tag = soup.find("img", class_="wideImage ng-star-inserted")
                if not image_tag:
                    image_cont = soup.find("div", class_="event-image")
                    image_tag = image_cont.find("img",class_='bg')
                else:
                    image_cont = image_cont = soup.find("div", class_="event-image wide-image")
                    image_tag = image_cont.find("img")

                image_path = ""
                if image_tag and image_tag.get("src"):
                    img_url = image_tag["src"]
                    try:
                        self.driver.get(img_url)
                        time.sleep(1)  

                        img_element = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.TAG_NAME, "img"))
                        )

                        img_filename = f"{uuid.uuid4()}.png"
                        img_path = os.path.join(image_folder, img_filename)

                        img_element.screenshot(img_path)

                    except Exception as e:
                        print(f"Görsel screenshot alınamadı: {e}")
                        img_path = ""
                else:
                    img_path = ""

                for div in soup.find_all("div", class_="performance-listing")[:5]:
                    icondiv = div.find('div', class_="date-box")
                    icon_text = icondiv.find("mat-icon").text.strip() if icondiv and icondiv.find("mat-icon") else ""

                    if icon_text == "calendar_month":
                        day = "Birden Fazla Tarih"
                        month = ""
                    else:
                        day = div.find("span", class_="day").text if div.find("span", class_="day") else ""
                        month = div.find("span", class_="month").text if div.find("span", class_="month") else ""

                    hour = div.find("span", class_="time").text if div.find("span", class_="time") else ""
                    name = div.find("span", class_="event-name").text if div.find("span", class_="event-name") else h1
                    map_ = soup.find("div", class_="performance-listing-venue").text if soup.find("div", class_="performance-listing-venue") else " "
                    print(f"Kaydedilen: {name} | {day} {month} {hour} | {map_} | {link}")

                    all_data.append({
                        'Day': day,
                        'Month': month,
                        'Hour': hour,
                        'Name': name,
                        'Map': map_,
                        'h1': h1,
                        'link': link,
                        'id': org_id,
                        'website': "Biletix",
                        'Image_Path': image_path
                    })
                    counter += 1

                if counter >= 70:
                    break

            except Exception as e:
                print(f"Error processing {link}: {e}")
                continue

        df = pd.DataFrame(all_data)
        df.to_csv(self.file_path, index=False, encoding='utf-8-sig')
        df.to_excel(self.file_path.replace(".csv", ".xlsx"), index=False, engine='openpyxl')


