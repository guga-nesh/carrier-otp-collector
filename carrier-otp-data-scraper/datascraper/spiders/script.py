import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import os
import time
import zipfile
import shutil



class ScriptSpider(scrapy.Spider):
    name = "script"
    allowed_domains = ["transtats.bts.gov"]
    
    # Key in your download directory and target directory that you want the .csv file to go to:
    download_dir = "/path/to/your/downloads/folder"
    target_dir = "/path/to/your/target/folder"

    # Key in year and month you want to scrape
    YEAR = 2024
    MONTH_START = 1
    MONTH_END = 1

    def start_requests(self):
        """
        Initiates a request to the specified URL using Selenium and waits for a specific element to be clickable.
        
        Yields:
            SeleniumRequest: A request to the specified URL with a callback to the `parse` method and a wait condition 
            for the 'Download' button to be clickable.
        """

        url = "https://www.transtats.bts.gov/DL_SelectFields.aspx?gnoyr_VQ=FGJ&QO_fu146_anzr="

        yield SeleniumRequest(
            url=url,
            callback=self.parse,
            wait_time=30,
            wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']#btnDownload")),
        )

    def wait_for_download_completion(self, filename, month, year):
        """
        Waits for the completion of the file download by monitoring the file system.

        Args:
            filename (str): The name of the file being downloaded.
            month (int): The month for which the file is being downloaded.
            year (int): The year for which the file is being downloaded.

        Raises:
            TimeoutException: If the download exceeds the specified timeout.
        """

        download_filepath = os.path.join(self.download_dir, filename)
        temp_filepath = download_filepath + ".crdownload"  # chrome's temporary download extension

        timeout = time.time() + 600 # 10-min timeout for large downloads
        # wait until the ZIP file is fully downloaded (i.e., without .crdownload)
        while os.path.exists(temp_filepath) or not os.path.exists(download_filepath):
            time.sleep(5)  # sleep briefly to allow the download to complete
            if time.time() > timeout:
                raise TimeoutException(f"Download for {month}_{year} took too long and timed out.")
        self.log(f"Downloaded {month}_{year} successfully")

    def delete_zip_file(self, zip_filepath):
        """
        Deletes the specified ZIP file from the download directory, with retry logic for handling file permissions.
        
        Args:
            zip_filepath (str): The file path of the ZIP file to delete.
        """
        
        # delete zip_file from download dir
        retries = 3
        for attempt in range(retries):
            try:
                if os.path.exists(zip_filepath):
                    os.remove(zip_filepath)
                    self.log(f"ZIP file {zip_filepath} deleted successfully")
                break
            except PermissionError:
                time.sleep(1)
                self.log(f"Retrying to delete ZIP file: {zip_filepath}")

    def process_zip_file(self, zip_filename, month, year):
        """
        Extracts the contents of the ZIP file and renames the extracted files before moving them to the target directory.
        
        Args:
            zip_filename (str): The name of the ZIP file to process.
            month (int): The month of the data.
            year (int): The year of the data.

        Raises:
            Exception: Any exception that occurs during the processing of the ZIP file is caught and logged.
        """

        zip_filepath = os.path.join(self.download_dir, zip_filename)
        try:
            with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
                zip_ref.extractall(self.download_dir)
            
            # iterate through extracted files (if multiple files exist in the ZIP)
                for extracted_file in zip_ref.namelist():
                    
                    # construct new filename based on year and month
                    new_filename = f"{month}_{year}.csv"
                    extracted_filepath = os.path.join(self.download_dir, extracted_file)
                    new_filepath = os.path.join(self.target_dir, new_filename)

                    # rename and move the extracted file to the target directory
                    shutil.move(extracted_filepath, new_filepath)
                    self.log(f"File {extracted_file} renamed and moved to {new_filepath}")
        except Exception as e:
            self.log(f"Error processing ZIP file: {e}")
            raise e
        finally:
            self.delete_zip_file(zip_filepath)

    def download_file(self, driver, year, month):
        """
        Downloads a CSV file for the specified year and month by interacting with the web interface.

        Args:
            driver (WebDriver): The Selenium WebDriver controlling the browser.
            year (int): The year for which the data is being downloaded.
            month (int): The month for which the data is being downloaded.

        Raises:
            Exception: If an error occurs during the download or processing, it is logged and re-raised.
        """
        try:
            
            # since this website takes more than 5 minutes (the default selenium timeout) to start the download for a file,
            # the page load timeout and script load timeout is set to 15 minutes to the script will not timeout
            driver.set_page_load_timeout(900)
            driver.set_script_timeout(900)
            
            # select year and month from dropdowns
            year_dropdown_elem = driver.find_element(By.ID, 'cboYear')
            month_dropdown_elem = driver.find_element(By.ID, 'cboPeriod')
            if year_dropdown_elem.tag_name == 'select' and month_dropdown_elem.tag_name == 'select': 
                year_dropdown = Select(year_dropdown_elem)
                month_dropdown = Select(month_dropdown_elem)
                year_dropdown.select_by_value(str(year))
                month_dropdown.select_by_value(str(month))
            
            # download CSV file
            download_button = driver.find_element(By.ID, "btnDownload")
            download_button.click()
            self.log(f"Download button for {month}_{year} clicked.")

            # process downloaded zip folder
            zip_filename = f"DL_SelectFields.zip"

            self.wait_for_download_completion(zip_filename, month, year)
            self.process_zip_file(zip_filename, month, year)
        except Exception as e:
            self.log(f"Error while downloading for {year}-{month}: {str(e)}")
            raise e

    def parse(self, response):
        """
        Parses the response from the initial request and prepares the page for data download.

        Args:
            response (Response): The response object from the SeleniumRequest that includes the driver.
        """
        
        # get driver
        driver = response.request.meta["driver"]
        
        # define timeout
        wait = WebDriverWait(driver, timeout=60)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']#btnDownload")))
        
        # uncheck pre-checked checkboxes
        to_be_unchecked = [
            "ORIGIN_AIRPORT_ID", "ORIGIN_AIRPORT_SEQ_ID", "ORIGIN_CITY_MARKET_ID",
            "DEST_AIRPORT_ID", "DEST_AIRPORT_SEQ_ID", "DEST_CITY_MARKET_ID"
        ]
        for checkbox_id in to_be_unchecked:
            checkbox = driver.find_element(By.ID, checkbox_id)
            if checkbox.tag_name == 'input' and checkbox.get_attribute("type") == 'checkbox':
                if checkbox.is_selected():
                    checkbox.click()
        
        # check checkboxes of features required
        checkboxes = [
            'YEAR', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK', 'FL_DATE', # time period
            'OP_UNIQUE_CARRIER', 'OP_CARRIER_FL_NUM', 'TAIL_NUM', # airline
            'ORIGIN', 'ORIGIN_CITY_NAME',  # origin
            'DEST', 'DEST_CITY_NAME',  # destination
            'DEP_TIME', 'CRS_DEP_TIME', 'DEP_DELAY', 'TAXI_OUT',   # departure performance 
            'ARR_TIME', 'CRS_ARR_TIME', 'ARR_DELAY', 'TAXI_IN',  # arrival performance
            'CANCELLED', 'CANCELLATION_CODE', 'DIVERTED', # cancellations and diversions
            'ACTUAL_ELAPSED_TIME', 'CRS_ELAPSED_TIME', 'AIR_TIME', 'DISTANCE', # flight summaries
            'CARRIER_DELAY', 'WEATHER_DELAY', 'NAS_DELAY', 'SECURITY_DELAY', 'LATE_AIRCRAFT_DELAY' # cause of delay
        ]
        for checkbox_id in checkboxes:
            checkbox = driver.find_element(By.ID, checkbox_id)
            if checkbox.tag_name == 'input' and checkbox.get_attribute('type') == 'checkbox':
                if not checkbox.is_selected():
                    checkbox.click()

        for month in range (self.MONTH_START, self.MONTH_END+1):
                self.download_file(driver, self.YEAR, month)