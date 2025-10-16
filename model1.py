''''
This model is just to open the site and scrape basic details like name, price, and image URL from nnnnow website.
This does not scroll, just scrapes the products visible on the first page.

Working:
1. Opens the nnnnow website and closes any popups.
2. Searches for the product given by the user.
3. Scrapes the required details from each product and stores them in a dictionary.
4. Exports the data to a CSV file named "Productlist_<product_name>.csv".

'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time 

product_name = input("Enter Product :")
product_number = input("Enter Product Number(Enter -1 for all products) :")

# Use webdriver-manager to automatically manage ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver.get("https://www.nnnow.com/")
time.sleep(5)

data = []

# Step1 - Close all extra windows
main_window = driver.current_window_handle
for handle in driver.window_handles:
    if handle != main_window:
        driver.switch_to.window(handle)
        driver.close()
driver.switch_to.window(main_window)

# Step2 - Close popups
try:
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "crossIcon"))
    ).click()
except:
    pass

wait = WebDriverWait(driver, 10)
search_input = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input.nwc-inp.nw-searchbar-input"))
)

search_input.clear()
search_input.send_keys(product_name)
search_input.send_keys(Keys.RETURN)
time.sleep(5)

productlist = WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.nwc-grid-col.nw-productlist-eachproduct"))
)


productlist = driver.find_elements(By.CSS_SELECTOR, "div.nw-productlist-eachproduct")

data = []
for product in productlist:
    try:
        # 1️⃣ Name
        name = product.find_element(By.CSS_SELECTOR, "div.nw-productview-producttitle").text.strip()

        # 2️⃣ URL
        url = product.find_element(By.CSS_SELECTOR, "a.nw-productview").get_attribute("href")

        # 3️⃣ Image
        img = product.find_element(By.CSS_SELECTOR, "img.nwc-lazyimg").get_attribute("src")

        data.append({"Name": name, "URL": url, "Image": img})
    except Exception as e:
        print("Skipped a product due to:", e)
        continue


df = pd.DataFrame(data)
df.to_csv(f"Productlist_{product_name}.csv", index=False, encoding="utf-8")
print("Done")
driver.quit()
