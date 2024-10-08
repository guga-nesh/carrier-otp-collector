# Carrier On-Time Performance Scraper - Automated Data Collection from a Dynamic Website

This project automates the process of scraping data from a dynamic website **(transtats.bts.gov)** using checkboxes, dropdowns, and a download button to retrieve files. Built with Scrapy and Selenium, it efficiently extracts and downloads CSV data files for specific months and years. With this tool, you can retrieve the latest data on Carrier On-Time Performance in the US from the Bureau of Transportation Statistics.

![](/carrier-otp-data-scraper/carrier-otp-collector.png)

## Tools Used

- Scrapy: A Python-based web scraping framework.
- Selenium: For interacting with dynamic web elements (e.g., checkboxes, dropdowns).
- ChromeDriver: To automate browser actions using Selenium.
- Python: For scripting and handling file operations.

## Features

- Automated selection of specific data features via checkboxes and dropdowns.
- Customizable year and month selection for retrieving data.
- Downloads data files and extracts CSV content.
- Renames and organizes downloaded files in a target directory.
- Handles timeouts, retries, and exceptions for robust operation.

## Process of Implementation

- **Initial Setup:** Integrated Scrapy with Selenium using the `scrapy-selenium` middleware to handle dynamic content.
- **Web Element Interaction:** Automated browser to interact with checkboxes and dropdowns to select required features and time range.
- **Data Download:** Used Selenium to click the "Download" button and wait for file to be downloaded.
- **File Handling:** Implemented logic to extract downloaded ZIP files, rename CSV files by month and year, and move them to a target directory.
- **Error Handling:** Incorporated checks for timeouts, retries, and safe deletion of files to ensure smooth operation.

## How to Run the Project

1. **Install Dependencies:**
   - Clone the repository and navigate to the project directory.
   - Set up a virtual environment like so:
   <br>

   ```bash
   python -m venv myenv
   cd myenv
   .\Scripts\activate

   # You can deactivate the virtual environment with this command:
   deactivate
   ```

   - Install Dependencies:
   <br> `pip install -r requirements.txt`
2. **Set up ChromeDriver:**
   - Ensure that ChromeDriver is installed and compatible with your Chrome version.
   - Update the `SELENIUM_DRIVER_EXECUTABLE_PATH` in Scrapy settings:
   <br> `"carrier-otp-collector/carrier-otp-data-scraper/datascraper/settings.py"`
3. **Run the Spider:**
   - `cd` into `"carrier-otp-collector/carrier-otp-data-scraper/datascraper/spiders"`
   - To start the scraping process, run the following Scrapy command in the terminal:
   <br> `scrapy crawl script`
4. **Customization:**
   - Modify `script.py` to change the year and months you want to scrape.
   - The default directories for downloads and extracted files can be updated in `script.py`.

## Video Demo

Watch the demo of the project here.
