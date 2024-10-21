import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Data contract definition
data_contract = {
    'fields': [
        {'name': 'Player', 'required': True},
        {'name': 'Format', 'required': True},
        {'name': 'Runs', 'required': True},
        {'name': 'Centuries', 'required': False},
        {'name': 'Fifties', 'required': False},
    ]
}



class DataExtractor:
    def __init__(self, url):
        self.url = url

    def extract(self):
        # Set up Selenium WebDriver in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the driver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.url)
        time.sleep(5)  # Wait for the page to load completely

        # XPath to find the table rows
        rows = driver.find_elements(By.XPATH, '//table//tr')

        data = []
        for row in rows[1:]:  # Skip the header
            cols = row.find_elements(By.XPATH, './/td')
            if len(cols) >= 5:  # Ensure there are enough columns
                data.append({
                    'Player': cols[0].text.strip(),
                    'Format': cols[1].text.strip(),
                    'Runs': int(cols[2].text.strip().replace('*','').replace(',', '')),
                    'Centuries': int(cols[3].text.strip()) if cols[3].text.strip() else 0,
                    'Fifties': int(cols[4].text.strip()) if cols[4].text.strip() else 0,
                })
        driver.quit()
        return pd.DataFrame(data)

class DataTransformer:
    def __init__(self, data):
        self.data = data

    def transform(self):
        # Calculate century conversion rate
        self.data['Century Conversion Rate'] = (
            self.data['Centuries'] / (self.data['Centuries'] + self.data['Fifties'].replace(0, pd.NA))
        ).fillna(0).round(4)
        return self.data

class DataValidator:
    def __init__(self, data, data_contract):
        self.data = data
        self.data_contract = data_contract

    def validate(self):
        for field in self.data_contract['fields']:
            if field['required'] and field['name'] not in self.data.columns:
                raise ValueError(f"Missing required field: {field['name']}")
            if field['name'] in self.data.columns and self.data[field['name']].isnull().any():
                raise ValueError(f"Field {field['name']} contains null values.")

class ETLPipeline:
    def __init__(self, url, data_contract):
        self.url = url
        self.data_contract = data_contract
        self.extractor = DataExtractor(url)
        self.transformer = None
        self.validator = None

    def run(self):
        # Extract
        data = self.extractor.extract()
        
        # Validate
        self.validator = DataValidator(data, self.data_contract)
        self.validator.validate()
        
        # Transform
        self.transformer = DataTransformer(data)
        transformed_data = self.transformer.transform()
        
        return transformed_data

if __name__ == "__main__":
    url = "https://www.espncricinfo.com/records/most-runs-in-career-223646"
    etl_pipeline = ETLPipeline(url, data_contract)
    final_data = etl_pipeline.run()
    print(final_data)
