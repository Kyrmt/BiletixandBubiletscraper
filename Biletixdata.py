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


    def scrape_data(self, links):
        # klasor_yolu = r"C:\Users\Kayra\Desktop\Napak\Photos"
        all_data = []
        bannedplaces = [
        "Oran Açık Hava Sahnesi",
        "Jolly Joker Ankara",
        "Masterpiece Ankara",
        "6:45 KK Ankara",
        "Çukurambar Kültür ve Sanat",
        "Congresium Ankara",
        "IF Performance Hall",
        "Şato Yazar Sahne",
        "CerModern",
        "Yenimahalle Nazım Hikmet KM",
        "JW Marriott Hotel Ankara",
        "Çayyolu Sahne",
        "Masterpiece Ümitköy",
        "Kinesis Stage & Art Space",
        "Kulis Sanat Tiyatrosu Panora",
        "Fade Stage & Coffee",
        "Yıldız Kenter Tiyatro Salonu",
        "CSO Ada Ankara Açıkhava",
        "Kulüp Müjgan",
        "Berlin Cafe Pub",
        "Altı Üstü Bar",
        "CSO Ada Ankara - Ana Salon",
        "Route Ankara",
        "Göksu Parkı",
        "Çankaya Sahne",
        "IF Performance Hall Tepe Prime",
        "4 Mevsim Tiyatro Sln",
        "Milyon Performance Hall Ankara",
        "Erimtan Arkeoloji ve Sanat Müzesi",
        "Actor Studio Panora AVM",
        "Nergiz Gösteri Merkezi",
        "Coffee Up Bahçelievler",
        "Necmettin Erbakan Kongre Merkezi",
        "ODTÜ MD Vişnelik Çim Amfi",
        "Göksu No: 5 Sahne",
        "Çağdaş Sanatlar Merkezi",
        "Quito Coffee",
        "Atılım Üniversitesi Amfi Tiyatro",
        "Ankara Sanat Tiyatro",
        "Yılmaz Güney Sahnesi",
        "Yaşar Kemal Kültür ve Sanat Merkezi",
        "Editör Dükkan",
        "Gökyay Vakfı Satranç Müzesi",
        "Ted Üniversitesi Kolej Kampüsü",
        "Hill 151",
        "Batıkent Meydan AVM Tiyatro Salonu",
        "IF Performance Hall"
]

        counter = 0
        for link in links:
            
            try:
                self.driver.set_page_load_timeout(15)  
                time.sleep(0.9)  
                self.driver.get(link)
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "performance-listing")))
                except Exception as e:
                    print(f"Timed out waiting for performance listings on {link}")
                    continue
                    
                html = self.driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                
                h1 = soup.find("h1").text if soup.find("h1") else " "

                if h1 in bannedplaces:
                    continue

                map_ = soup.find("div", class_="performance-listing-venue").text if soup.find("div", class_="performance-listing-venue") else " "
                org_id = uuid.uuid4()
                for div in soup.find_all("div", class_="performance-listing"):
                    if div.find("mat-icon"):  
                        continue
                    hour_div = div.find("div", class_="info-group")
                    hour = hour_div.find("span","time ng-star-inserted").text if  hour_div.find("span","time ng-star-inserted") else ""
                    day = div.find("span", class_="day").text if div.find("span", class_="day") else " "
                    month = div.find("span", class_="month").text if div.find("span", class_="month") else " "
                    name = div.find("span", class_="event-name").text if div.find("span", class_="event-name") else " "
                    
                    print(f"Kaydedilen: {name} | {day} {month} {hour} | {map_} | {org_id}")
                    
                    new_data = {
                        'Day': day,
                        'Month': month,
                        'Hour': hour,
                        'Name': name,
                        'Map': map_,
                        'h1': h1,
                        'link': link,
                        'id' : org_id,
                        'website': "Biletix"
                    }
                    all_data.append(new_data)
                    counter += 1
                if counter >= 40:
                    self.driver.quit()
                    break
            except Exception as e:
                print(f"Error processing {link}: {e}")
                continue

        df = pd.DataFrame(all_data, columns=["Day", "Month", "Hour", "Name", "Map", "h1", "link","id", "website"])
        df.to_csv(self.file_path, mode='w', header=True, index=False, encoding='utf-8-sig')
        df.to_excel(self.file_path.replace(".csv", ".xlsx"), index=False, engine='openpyxl')

