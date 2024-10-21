"""
ETL Pipeline for Cricket Data Extraction, Transformation, and Validation

Author: Dayananda Challa
Date: 19-10-2023
Version: 1.0

This script defines an ETL (Extract, Transform, Load) pipeline that scrapes cricket player statistics 
from a specified URL, validates the data using SODA checks, and transforms the data for further analysis.

Classes:
1. DataExtractor: 
   - Responsible for extracting data from a webpage using Selenium. 
   - Retrieves player statistics from a table and converts it into a Pandas DataFrame.

2. DataTransformer: 
   - Handles the transformation of the extracted data.
   - Calculates additional metrics such as the Century Conversion Rate.

3. DataValidator: 
   - Validates the extracted DataFrame against a set of predefined checks using SODA.
   - Ensures the integrity and completeness of the data before transformation.

4. ETLPipeline: 
   - Orchestrates the entire ETL process.
   - Manages the flow of data extraction, validation, and transformation.

Dependencies:
- Selenium: For web scraping dynamic content from web pages.
- Pandas: For data manipulation and analysis.
- PyYAML: For parsing YAML files.
- Dask: For parallel computing with Pandas.
- SODA: For data validation checks.

Usage:
- Define the URL of the webpage containing the data.
- Instantiate the ETLPipeline with the URL and call the `run()` method to execute the pipeline.
- The final transformed DataFrame will be printed to the console.

Note: Ensure the required dependencies are installed and the Selenium WebDriver is set up correctly before running the script.
"""

import pandas as pd
import yaml
from soda.scan import Scan  # Import Soda's Scan functionality
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import dask

# Disable automatic string conversion in Dask to avoid potential issues
dask.config.set({"dataframe.convert-string": False})


# Define the data contract in YAML format for Soda checks
data_contract_yaml = """
checks:
  - name: player_check
    type: required
    column: Player
  - name: format_check
    type: required
    column: Format
  - name: runs_check
    type: required
    column: Runs
  - name: centuries_check
    type: optional
    column: Centuries
  - name: fifties_check
    type: optional
    column: Fifties
"""

# Load the Soda checks from the YAML
data_contract = yaml.safe_load(data_contract_yaml)

class DataExtractor:
    """Class for extracting data from a specified URL using Selenium."""
    def __init__(self, url):
        """Initialize with the URL to scrape."""
        self.url = url

    def extract(self):
        """Extract data from the webpage and return it as a DataFrame."""
        # Set up Selenium WebDriver in headless mode (no GUI)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run Chrome in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize the driver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.url)
        time.sleep(5)  # Wait for the page to load completely

        # Find all table rows on the page
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
        # Close the browser
        driver.quit()
        # Return the data as a DataFrame
        return pd.DataFrame(data)

class DataTransformer:
    """Class for transforming the extracted data."""
    def __init__(self, data):
        """Initialize with the DataFrame to transform."""
        self.data = data

    def transform(self):
        """Perform data transformations and return the modified DataFrame."""
        # Calculate century conversion rate
        self.data['Century Conversion Rate'] = (
            self.data['Centuries'] / (self.data['Centuries'] + self.data['Fifties'].replace(0, pd.NA))
        ).fillna(0).round(4) # Fill NaN values with 0 and round to 4 decimal places
        return self.data

class DataValidator:
    """Class for validating data using SODA checks."""
    def __init__(self, data, data_contract):
        """Initialize with the DataFrame to validate."""
        self.data = data
        self.data_contract = data_contract

    def validate(self):
        """Validate the DataFrame against defined checks and print results."""
        # Initialize the SODA scan
        scan = Scan()

        # Define SODA checks for data validation
        sodacl_checks = """
        checks for df:
          - missing_count(Player) = 0
          - missing_count(Format) = 0
          - missing_count(Runs) = 0
          - max(Centuries) >= 0
          - min(Fifties) >= 0
        """
        
        # Add checks to the scan
        scan.add_sodacl_yaml_str(sodacl_checks)
        # Add the DataFrame to the scan for validation
        scan.add_pandas_dataframe("df", self.data)  # Pass the DataFrame to Soda for validation
        
        # Execute the scan
        scan.execute()

        # Retrieve the results of the scan
        scan_result = scan.get_scan_results()
        
        print(scan_result)

class ETLPipeline:
    """Class representing the ETL pipeline for extracting, validating, and transforming data."""
    def __init__(self, url, data_contract):
        """Initialize with the URL to extract data from."""
        self.url = url
        self.data_contract = data_contract
        self.extractor = DataExtractor(url)
        self.transformer = None
        self.validator = None

    def run(self):
        """Run the ETL pipeline: extract, validate, and transform data."""
        # Extract data from the specified URL
        data = self.extractor.extract()
        
        # Validate the extracted data
        self.validator = DataValidator(data, self.data_contract)
        self.validator.validate()
        
        # Transform the validated data
        self.transformer = DataTransformer(data)
        transformed_data = self.transformer.transform()
        
        return transformed_data

if __name__ == "__main__":
    # Define the URL to scrape data from
    url = "https://www.espncricinfo.com/records/most-runs-in-career-223646"

    # Create an instance of the ETLPipeline with the specified URL
    etl_pipeline = ETLPipeline(url, data_contract)

    # Run the ETL pipeline and get the final transformed data
    final_data = etl_pipeline.run()

    # Print the final transformed data
    print(final_data)
