from bubiletdata import BuBiletScraper
from Biletixdata import BiletixScraper
file_path = r"C:\Users\Kayra\Desktop\Napak\BuBiletDatabase.csv"
file_path = r"C:\Users\Kayra\Desktop\Napak\BiletixDatabase.csv"


# Bubilet = BuBiletScraper(file_path)
# links = Bubilet.fetch_links()
# Bubilet.scrape_data(links)
# Bubilet.close()

Biletix = BiletixScraper(file_path)
links = Biletix.get_links()
Biletix.scrape_data(links)
Biletix.close()