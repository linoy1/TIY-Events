import os
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
app = Flask(__name__)

@app.route('/')
def scrape_events():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 5)

    try:
        driver.get("https://www.ramat-gan.muni.il/events/")
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event_unit")))
        event_units = driver.find_elements(By.CLASS_NAME, "event_unit_top")
        event_units_bottom = driver.find_elements(By.CLASS_NAME, "event_unit_bottom")

        events = []

        for event_unit, event_unit_bottom in zip(event_units, event_units_bottom):
            title = event_unit.find_element(By.CLASS_NAME, "ng-binding").text
            location = event_unit.find_element(By.CLASS_NAME, "event_unit_location").text
            address = event_unit.find_element(By.CLASS_NAME, "event_unit_address").text

            try:
                date = event_unit_bottom.find_element(By.CSS_SELECTOR, ".event_unit_pill").text
            except NoSuchElementException:
                try:
                    date = event_unit_bottom.find_element(By.CSS_SELECTOR, ".event_unit_date").text
                except NoSuchElementException:
                    date = ""

            events.append({
                "title": title,
                "location": location,
                "address": address,
                "date": date
            })

        # Click the "Load More Events" button and wait for new events to appear
        while True:
            try:
                load_more_button = driver.find_element(By.CLASS_NAME, "load_more")
                load_more_button.click()
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event_unit")))
                new_event_units = driver.find_elements(By.CLASS_NAME, "event_unit_top")
                new_event_units_bottom = driver.find_elements(By.CLASS_NAME, "event_unit_bottom")

                for event_unit, event_unit_bottom in zip(new_event_units, new_event_units_bottom):
                    title = event_unit.find_element(By.CLASS_NAME, "ng-binding").text
                    location = event_unit.find_element(By.CLASS_NAME, "event_unit_location").text
                    address = event_unit.find_element(By.CLASS_NAME, "event_unit_address").text

                    try:
                        date = event_unit_bottom.find_element(By.CSS_SELECTOR, ".event_unit_date").text
                    except NoSuchElementException:
                        date = ""

                    events.append({
                        "title": title,
                        "location": location,
                        "address": address,
                        "date": date
                    })

                if new_event_units == []:
                    break
            except:
                break
    finally:
        driver.quit()

    return jsonify(events)

if __name__ == '__main__':
    app.run()
