# LLM-Powered Web Scraper

This project is a Streamlit web application that combines dynamic web scraping with a large language model (LLM) to extract structured data from web pages. It uses Selenium and BeautifulSoup for content extraction and cleaning, and leverages the Hugging Face Inference API for data parsing based on user-specified instructions.

## Features

- **Dynamic Web Scraping:**  
  Uses Selenium (with a headless Edge WebDriver by default) to load and scrape pages that render content dynamically via JavaScript.

- **Content Extraction & Cleaning:**  
  Extracts the webpage's body content and cleans it using BeautifulSoup by removing unnecessary elements like scripts, styles, and iframes.

- **Custom Data Parsing:**  
  Integrates an LLM (via Hugging Face Inference API) to convert cleaned content into well-formatted tables based on detailed user instructions.

- **Interactive User Interface:**  
  Built with Streamlit, the app allows you to:
  - Input a URL to scrape
  - View the extracted/cleaned content
  - Provide custom data extraction instructions
  - Display parsed data in a table
  - Download results as CSV

## Prerequisites

- Python 3.7+
- [pip](https://pip.pypa.io/)
- Microsoft Edge WebDriver (or modify `scrape.py` for another browser)
- Hugging Face API key
- create a .env file and place your hugging face API in it.
