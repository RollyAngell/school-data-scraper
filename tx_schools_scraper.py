from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import random
import logging
import os
from datetime import datetime

# Configuration
URL = "https://txschools.gov/?view=schools&lng=en"
MAX_PAGES = 30  # Change to a number (e.g., 10) to limit pages, or leave as None for all pages.

# Logging configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# Configure Selenium driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in background
    return webdriver.Chrome(options=options)

# Function to retry operations in case of failures
def retry_operation(func, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay)
    return None

# Select grade level in filter
def select_grade_level(driver, grade):
    def _select():
        grade_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Select a grade level']"))
        )
        grade_input.click()
        
        options_list = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//li[contains(text(), '{}')]".format(grade)))
        )
        
        if options_list:
            options_list[0].click()
            print(f"🎓 Grade selected: {grade}")
            return True
        return False
    
    return retry_operation(lambda: _select())

# Function to extract school links from a page
def extract_school_links(driver, page_number):
    school_links = []

    try:
        # Aumentar el timeout para páginas más lentas
        WebDriverWait(driver, 20).until(  # Aumentado de 10 a 20 segundos
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Find all table rows
        rows = driver.find_elements(By.XPATH, "//table/tbody/tr")
        total_schools = len(rows)
        
        print(f"📄 Page {page_number} - Schools found: {total_schools}")

        # Extract links for all schools on the page
        for row in rows:
            try:
                link_element = row.find_element(By.XPATH, ".//a")
                school_link = link_element.get_attribute("href")
                school_links.append(school_link)
                print(f"🔗 School link found: {school_link}")
            except Exception as e:
                print(f"❌ Error extracting link from row: {e}")
                continue

    except Exception as e:
        print(f"❌ No schools found in table on page {page_number}: {e}")

    return school_links

# Data quality checks
def validate_school_data(data):
    validation_results = {
        "is_valid": True,
        "issues": [],
        "score": 0
    }
    
    # List of valid US state abbreviations
    valid_states = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC'
    }
    
    # Phone number format validation
    def is_valid_phone(phone):
        # Remove all non-numeric characters
        digits = ''.join(filter(str.isdigit, phone))
        return len(digits) == 10

    # Website URL validation
    def is_valid_url(url):
        return url.startswith(('http://', 'https://'))

    # School name validation
    def is_valid_school_name(name):
        return len(name) >= 3 and any(c.isalpha() for c in name)
    
    required_fields = {
        "School Name": "Missing School Name",
        "Address 1": "Missing Address",
        "City": "Missing City",
        "State": "Missing State",
        "Zip": "Missing ZIP",
        "Phone": "Missing Phone",
        "School Website": "Missing Website",
        "District": "Missing District",
        "Grades Served": "Missing Grades",
        "Principal Name": "Missing Principal"
    }
    
    filled_fields = 0
    for field, message in required_fields.items():
        if data.get(field) and data[field] != "Not Found":
            value = data[field].strip()
            
            # Field-specific validations
            if field == "Zip":
                if not (value.isdigit() and len(value) == 5):
                    validation_results["issues"].append("Invalid ZIP format - must be 5 digits")
                    continue
                    
            elif field == "State":
                if value.upper() not in valid_states:
                    validation_results["issues"].append("Invalid state abbreviation")
                    continue
                    
            elif field == "Phone":
                if not is_valid_phone(value):
                    validation_results["issues"].append("Invalid phone number format")
                    continue
                    
            elif field == "School Website":
                if not is_valid_url(value):
                    validation_results["issues"].append("Invalid website URL format")
                    continue
                    
            elif field == "School Name":
                if not is_valid_school_name(value):
                    validation_results["issues"].append("Invalid school name format")
                    continue
                    
            elif field == "City":
                if not value.replace(" ", "").isalpha():
                    validation_results["issues"].append("City name should only contain letters")
                    continue
                    
            elif field == "Principal Name":
                if len(value.split()) < 2:
                    validation_results["issues"].append("Principal name should include first and last name")
                    continue
            
            filled_fields += 1
        else:
            validation_results["issues"].append(f"{field} not available")
    
    # Calculate score using integer division
    total_fields = len(required_fields)
    validation_results["score"] = (filled_fields * 100) // total_fields
    
    validation_results["is_valid"] = (validation_results["score"] == 100)
    
    return validation_results

# Extract data from individual school
def extract_school_data(driver, page_number):
    logger = logging.getLogger(__name__)
    data_fields = {
        "Page Number": str(page_number),
        "School Name": "Not Found",
        "Address 1": "Not Found",
        "Address 2": "Not Found",
        "City": "Not Found",
        "State": "Not Found",
        "Zip": "Not Found",
        "Phone": "Not Found",
        "Principal Name": "Not Found",
        "School Website": "Not Found",
        "District": "Not Found",
        "Grades Served": "Not Found",
        "Data Quality Score": 0,
        "Data Quality Issues": ""
    }
    
    xpath_mappings = {
        "School Name": ("//h1", "text"),
        "Address 1": ("//div[contains(@class, 'MuiGrid-grid-md-5')]/p[contains(b, 'ADDRESS:')]", "text", "ADDRESS:\n"),
        "Phone": ("//div[contains(@class, 'MuiGrid-grid-sm-4')]/p[contains(b, 'Phone:')]", "text", "Phone:\n"),
        "Principal Name": ("//div[contains(@class, 'MuiGrid-grid-sm-4')]/p[contains(b, 'Principal Name:')]", "text", "Principal Name:\n"),
        "School Website": ("//a[contains(@class, 'MuiButton-contained')]", "href"),
        "District": ("//span[contains(text(),'District:')]/b/a", "text"),
        "Grades Served": ("//span[contains(text(),'Grades Served:')]/b", "text")
    }
    
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        for field, (xpath, attr_type, *replace_text) in xpath_mappings.items():
            try:
                element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
                value = element.get_attribute("href") if attr_type == "href" else element.text
                if replace_text:
                    value = value.replace(replace_text[0], "")
                if value.strip():
                    data_fields[field] = value.strip()
            except:
                print(f"⚠️ {field} not found")
        
        # Procesar la dirección completa
        try:
            address_element = driver.find_element(By.XPATH, "//div[contains(@class, 'MuiGrid-grid-sm-4')]/p[contains(b, 'Address:')]")
            address_lines = address_element.text.replace("Address:\n", "").strip().split("\n")
            if len(address_lines) >= 2:
                data_fields["Address 2"] = address_lines[0]
                city_state_zip = address_lines[-1].split(", ")
                if len(city_state_zip) >= 2:
                    data_fields["City"] = city_state_zip[0].strip()
                    state_zip = city_state_zip[1].split()
                    if len(state_zip) == 2:
                        data_fields["State"] = state_zip[0]
                        data_fields["Zip"] = state_zip[1]
        except:
            print("⚠️ Address parsing failed")
            
        # Validate and add quality metrics
        validation_results = validate_school_data(data_fields)
        
        # Set the quality score and issues directly from validation results
        data_fields["Data Quality Score"] = validation_results["score"]
        data_fields["Data Quality Issues"] = ", ".join(validation_results["issues"]) if validation_results["issues"] else ""
        
        # Log quality information
        logger.info(f"School: {data_fields['School Name']}")
        logger.info(f"Quality Score: {data_fields['Data Quality Score']}")
        logger.info(f"Quality Issues: {data_fields['Data Quality Issues']}")
        
    except Exception as e:
        logger.error(f"❌ Error extracting data: {e}")
    
    return data_fields

# Function to create output directory if it doesn't exist
def ensure_output_directory(directory="output"):
    """Create output directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created output directory: {directory}")
    return directory

# Function to save data to CSV
def save_to_csv(data, filename):
    if not data:
        return
    
    # Create output directory
    output_dir = ensure_output_directory()
    
    # Create full path for the file
    full_path = os.path.join(output_dir, filename)
    
    # Calculate overall quality metrics
    total_schools = len(data)
    avg_quality_score = sum(float(school["Data Quality Score"]) for school in data) / total_schools
    schools_with_issues = sum(1 for school in data if school["Data Quality Issues"])
    
    # Add summary to log
    logger = logging.getLogger(__name__)
    logger.info("\n=== Data Quality Summary ===")
    logger.info(f"Total schools processed: {total_schools}")
    logger.info(f"Average quality score: {avg_quality_score:.2f}%")
    logger.info(f"Schools with quality issues: {schools_with_issues}")
    logger.info(f"Quality rate: {((total_schools - schools_with_issues) / total_schools) * 100:.2f}%")
    logger.info(f"Data saved to: {full_path}")
    
    # Save data to CSV file
    keys = data[0].keys()
    with open(full_path, mode='w', newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

# Function to navigate to the next page
def navigate_to_next_page(driver):
    try:
        print("🔄 Attempting to navigate to next page...")
        
        # Wait for table to fully update
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        # Navigate to specific page using JavaScript
        current_page = int(driver.find_element(By.CSS_SELECTOR, "button[aria-current='true']").text)
        next_page = current_page + 1
        
        # Find all pagination buttons
        pagination_buttons = driver.find_elements(By.CSS_SELECTOR, "nav[aria-label='pagination navigation'] button")
        
        # Find the button with the next page number
        next_button = None
        for button in pagination_buttons:
            if button.text.strip() == str(next_page):
                next_button = button
                break
        
        if not next_button:
            print(f"❌ Button for page {next_page} not found")
            return False
        
        # Make scroll and click
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)
        
        try:
            next_button.click()
            print(f"✅ Successfully navigated to page {next_page}")
        except Exception as click_error:
            print(f"⚠️ Error in normal click, trying with JavaScript")
            driver.execute_script("arguments[0].click();", next_button)
        
        time.sleep(3)
        return True
            
    except Exception as e:
        print(f"❌ Error al navegar: {str(e)}")
        return False

def get_all_school_links_first(driver):
    """
    Get all school links first and then process them
    """
    logger = logging.getLogger(__name__)
    all_links = []
    page_number = 1
    
    try:
        logger.info("🔍 Starting link collection...")
        
        # Apply filters only once
        for grade in ["Early Education", "Prekindergarten", "Kindergarten"]:
            if not select_grade_level(driver, grade):
                logger.warning(f"⚠️ Could not select grade: {grade}")
                continue
            time.sleep(random.uniform(1, 2))
        
        while True:
            logger.info(f"📃 Getting links from page {page_number}")
            links = extract_school_links(driver, page_number)
            
            if not links:
                logger.info("🏁 No more links found")
                break
                
            all_links.extend(links)
            logger.info(f"✅ Links found on page {page_number}: {len(links)}")
            
            if MAX_PAGES and page_number >= MAX_PAGES:
                logger.info("🏁 Maximum page limit reached")
                break
                
            if not navigate_to_next_page(driver):
                break
                
            page_number += 1
            time.sleep(random.uniform(2, 3))
            
    except Exception as e:
        logger.error(f"❌ Error collecting links: {str(e)}")
    
    logger.info(f"📊 Total links collected: {len(all_links)}")
    return all_links

def process_school_links(driver, links):
    """
    Process the list of school links
    """
    logger = logging.getLogger(__name__)
    all_school_data = []
    total_links = len(links)
    
    for index, link in enumerate(links, 1):
        try:
            logger.info(f"\n🏫 Processing school {index}/{total_links}: {link}")
            driver.get(link)
            time.sleep(random.uniform(1, 2))
            
            school_data = extract_school_data(driver, index)
            all_school_data.append(school_data)
            
            # Save progress every 10 schools
            if index % 10 == 0:
                save_progress(all_school_data, f"progress_batch_{index}.csv")
                
            logger.info(f"✅ Data extracted: {school_data['School Name']}")
            
        except Exception as e:
            logger.error(f"❌ Error processing school: {str(e)}")
            continue
            
        # Random pause between schools
        time.sleep(random.uniform(1, 3))
    
    return all_school_data

def save_progress(data, filename):
    """
    Guardar progreso parcial
    """
    output_dir = ensure_output_directory("progress")
    full_path = os.path.join(output_dir, filename)
    
    if data:
        keys = data[0].keys()
        with open(full_path, mode='w', newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)

def scrape_schools():
    logger = setup_logging()
    driver = setup_driver()
    
    try:
        logger.info("🚀 Starting scraping process...")
        driver.get(URL)
        time.sleep(random.uniform(2, 3))
        
        # Phase 1: Collect all links
        all_links = get_all_school_links_first(driver)
        
        if not all_links:
            logger.error("❌ No links found to process")
            return
            
        # Phase 2: Process the links
        logger.info("🔄 Starting link processing...")
        all_school_data = process_school_links(driver, all_links)
        
        # Save final results
        if all_school_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"schools_data_{timestamp}.csv"
            save_to_csv(all_school_data, csv_filename)
            logger.info(f"📂 Data saved to {csv_filename}")
            logger.info(f"📊 Total schools processed: {len(all_school_data)}")
        else:
            logger.warning("⚠️ No data to save")

    except Exception as e:
        logger.error(f"❌ General error: {str(e)}")
    
    finally:
        driver.quit()

# Run the script
if __name__ == "__main__":
    scrape_schools()