from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
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
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-dev-shm-usage")  # Important for Docker/CI environments
        
        # Configure timeouts
        self.service = Service("chromedriver.exe")
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        
        # Set various timeouts
        self.driver.set_page_load_timeout(30)  # Page load timeout
        self.driver.set_script_timeout(30)     # Script timeout

    def fetch_links(self, max_retries=3):
        links = []
        retries = 0
        while retries < max_retries:
            try:
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
            except TimeoutException:
                retries += 1
                print(f"Timeout occurred, retrying ({retries}/{max_retries})...")
                time.sleep(2)
            except Exception as e:
                print(f"Error fetching links: {e}")
                break
        return links

    def scrape_data(self, links, max_items=40):
        all_data = []
        counter = 0
        
        for link in links:
            if counter >= max_items:
                break
                
            retries = 0
            max_retries = 2
            
            while retries < max_retries:
                try:
                    print(f"Processing {link}...")
                    self.driver.get(link)
                    html = self.driver.page_source
                    soup = BeautifulSoup(html, "html.parser")
                    
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
                            'id': id,
                            'website': "Bubilet"
                        }
                        all_data.append(new_data)
                        print(f"Saved: {name} | {spanarray[0]} {spanarray[1]} | {spanarray[2]} | {price}")
                        counter += 1
                        break  # Success, break out of retry loop
                    else:
                        print(f"Incomplete data for {link}")
                        break
                        
                except TimeoutException:
                    retries += 1
                    print(f"Timeout occurred on {link}, retrying ({retries}/{max_retries})...")
                    time.sleep(2)
                except Exception as e:
                    print(f"Error processing {link}: {str(e)[:200]}")  # Truncate long error messages
                    break

            time.sleep(0.5)  # Gentle delay between requests

        if all_data:
            df = pd.DataFrame(all_data, columns=["Day", "Price", "Hour", "Name", "Map", "link", "id", "website"])
            df.to_csv(self.file_path, mode='w', header=True, index=False, encoding='utf-8-sig')
            try:
                df.to_excel(self.file_path.replace('.csv', '.xlsx'), index=False, engine='openpyxl')
            except Exception as e:
                print(f"Error saving Excel file: {e}")

    def close(self):
        try:
            self.driver.quit()
        except:
            pass