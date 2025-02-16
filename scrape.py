import selenium.webdriver as webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time

def scrape_website(website):
    print("Launching the browser...")
    
    edge_driver_path = "./msedgedriver.exe"
    
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--disable-gpu") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # Set window size for better rendering
    
    driver = None
    try:
        driver = webdriver.Edge(service=Service(edge_driver_path), options=options)
        driver.set_page_load_timeout(30)  # Set page load timeout
        
        print("Loading the website...")
        driver.get(website)
        
        # Wait for body element to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(("tag name", "body"))
        )
        
        # Scroll page to load dynamic content
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        html = driver.page_source
        if not html:
            print("Error: No HTML content retrieved.")
            return None
        return html
        
    except TimeoutException:
        print("Timeout waiting for page to load")
        return None
    except Exception as e:
        print(f"Scraping error: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def extract_body_content(html_content):
    if not html_content:
        print("Error: HTML content is None")
        return "No content available"
    
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'noscript', 'iframe']):
            element.decompose()
            
        body_content = soup.body
        return str(body_content) if body_content else "No body content found"
    except Exception as e:
        print(f"Error extracting content: {e}")
        return "Error processing content"

def clean_body_content(body_content):
    if not body_content:
        return ""
    
    try:
        soup = BeautifulSoup(body_content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        
        # Get text and remove excess whitespace
        text = soup.get_text(separator="\n")
        lines = []
        for line in text.split("\n"):
            line = line.strip()
            if line:  # Keep only non-empty lines
                lines.append(line)
        
        # Remove duplicate lines while preserving order
        seen = set()
        cleaned_lines = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    except Exception as e:
        print(f"Error cleaning content: {e}")
        return ""

def split_dom_content(dom_content, max_length=6000):
    if not dom_content:
        return []
    
    # Split content into chunks at sentence boundaries
    chunks = []
    current_chunk = ""
    
    for line in dom_content.split("\n"):
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
    