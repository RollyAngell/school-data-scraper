# School Data Scraper

## How can this code be run?

### Prerequisites
1. Python 3.x installed
2. Chrome browser installed
3. Required Python packages:
   - selenium
   - webdriver_manager

### Steps to Run
1. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv scraping-env

# Activate virtual environment
# On Windows:
scraping-env\Scripts\activate
# On macOS/Linux:
source scraping-env/bin/activate
```

2. Install dependencies:
```bash
pip install selenium webdriver_manager
```

3. Run the script:
```bash
python tx_schools_scraper.py
```

4. The script will generate:
   - A CSV file in the output directory (`output/schools_data_pages_1_to_X.csv`)
   - A log file with execution details (`scraper.log`)

### Output Structure
```
project/
│
├── tx_schools_scraper.py
├── test_tx_schools_scraper.py
├── scraper.log
│
└── output/
    └── schools_data_pages_1_to_X.csv
```

## Technologies Used

### Web Scraping Libraries

#### Selenium
**Advantages:**
- Handles dynamic JavaScript content
- Simulates real browser interaction
- Supports authentication and cookies
- Complex actions (clicks, scroll, etc.)
- Strong documentation and community
- Screenshot capability for debugging

**Disadvantages:**
- Slower than alternatives
- Higher resource consumption
- Requires webdriver installation
- More complex setup
- Not ideal for large-scale scraping

### Alternative Libraries Considered

#### BeautifulSoup
- Easy to use, great for static HTML
- Lightweight resource usage
- Cannot handle JavaScript
- Limited for dynamic sites

#### Scrapy
- High performance
- Built for large projects
- Asynchronous processing
- Steeper learning curve
- Limited JavaScript support

### Why Selenium?
- Site requires JavaScript handling
- Need for filter and pagination interaction
- Dynamic element loading
- Reliable data extraction
- Visual debugging capabilities

## What Data Quality was added?

### 1. Quality Score Calculation
- Added Data Quality Score (0-100%)
- Score based on 10 required fields:
  - School Name
  - Address 1
  - City
  - State
  - Zip
  - Phone
  - School Website
  - District
  - Grades Served
  - Principal Name

### 2. Quality Issues Tracking
- Added "Data Quality Issues" field in CSV
- Tracks missing or invalid data
- Issues are listed as comma-separated text

### 3. Quality Metrics in Log
- Total schools processed
- Average quality score
- Number of schools with issues
- Quality rate calculation

### 4. Data Validation

#### ZIP Code Validation
- Must contain exactly 5 digits
- Cannot contain letters or special characters
- Invalid ZIP codes will:
  - Generate a "Invalid ZIP format - must be 5 digits" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### State Validation
- Must be a valid US state abbreviation (including DC)
- State codes must be 2 letters
- Invalid states will:
  - Generate a "Invalid state abbreviation" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### Phone Number Validation
- Must contain exactly 10 digits
- Special characters and spaces are removed before validation
- Invalid phone numbers will:
  - Generate a "Invalid phone number format" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### Website URL Validation
- Must start with http:// or https://
- Basic URL format validation
- Invalid URLs will:
  - Generate a "Invalid website URL format" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### School Name Validation
- Must be at least 3 characters long
- Must contain at least one letter
- Invalid school names will:
  - Generate a "Invalid school name format" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### City Name Validation
- Must contain only letters and spaces
- Numbers and special characters are not allowed
- Invalid city names will:
  - Generate a "City name should only contain letters" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

#### Principal Name Validation
- Must include both first and last name
- Verified by checking for at least two words
- Invalid principal names will:
  - Generate a "Principal name should include first and last name" issue
  - Affect the overall Data Quality Score
  - Be listed in the Data Quality Issues field

### 5. Data Quality Impact
- Each validation failure reduces the overall quality score
- All fields must pass their respective validations for a 100% score
- Quality issues are tracked and reported in both:
  - The CSV output file
  - The detailed log file

## Future Improvements

### 1. Architecture Enhancements

#### Microservices Architecture
- Split functionality into separate services:
  - Scraping Service
  - Data Validation Service
  - Data Storage Service
  - API Service
- Benefits:
  - Better scalability
  - Easier maintenance
  - Independent deployment
  - Isolated failures

#### Data Pipeline Architecture
```
[Web Sources] -> [Scrapers] -> [Raw Data Lake] -> [Data Validation] -> [Data Warehouse] -> [API/Analytics]
```
- Raw data preservation
- Data versioning
- Audit trail
- Reprocessing capability

### 2. Orchestration

#### Apache Airflow
- Workflow management
- Task scheduling
- Dependency handling
- Retry mechanisms
- Monitoring dashboard
- Email notifications

#### Docker Containers
- Containerized services
- Environment consistency
- Easy deployment
- Resource isolation
- Scalability

### 3. Additional Tools

#### Testing
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests
- Data quality tests

## Running Unit Tests

### Prerequisites
1. Python 3.x installed
2. Project files in your directory:
   - `tx_schools_scraper.py` (main script)
   - `test_tx_schools_scraper.py` (test script)

### Step by Step Instructions

1. **Create a Test Environment:**
```bash
# Create virtual environment
python -m venv scraping-env

# Activate virtual environment
# On Windows:
scraping-env\Scripts\activate
# On macOS/Linux:
source scraping-env/bin/activate
```

2. **Install Required Packages:**
```bash
pip install unittest-xml-reporting
```

3. **Run the Tests:**
```bash
python test_tx_schools_scraper.py
```

### Test Results Understanding

The test suite includes 8 test cases that validate different aspects of the data:

1. **City Name Validation** (`test_invalid_city`)
   - Tests invalid formats: "Austin123", "Austin#", "123"
   - Validates city names contain only letters
   - Score: 90% for invalid entries

2. **Phone Number Validation** (`test_invalid_phone`)
   - Tests invalid formats: "123-456-789", "abcd-efg-hijk", "12345678901"
   - Validates 10-digit requirement
   - Score: 90% for invalid entries

3. **Principal Name Validation** (`test_invalid_principal_name`)
   - Tests invalid formats: "John", "J", "Not Found"
   - Validates first and last name requirement
   - Score: 90% for invalid entries

4. **School Name Validation** (`test_invalid_school_name`)
   - Tests invalid formats: "AB", "123", "Not Found"
   - Validates minimum length and letter requirement
   - Score: 90% for invalid entries

5. **State Validation** (`test_invalid_state`)
   - Tests invalid formats: "XX", "ABC", "A", "12"
   - Validates US state code requirement
   - Score: 90% for invalid entries

6. **Website URL Validation** (`test_invalid_website`)
   - Tests invalid formats: "test.com", "ftp://test.com", "not-a-url"
   - Validates proper URL format
   - Score: 90% for invalid entries

7. **ZIP Code Validation** (`test_invalid_zip_code`)
   - Tests invalid formats: "1234", "123456", "abcde", "12a45"
   - Validates 5-digit requirement
   - Score: 90% for invalid entries

8. **Valid School Data** (`test_valid_school_data`)
   - Tests complete valid entry
   - Score: 100% for valid entry

### Test Output Example
```
----------------------------------------------------------------------
Ran 8 tests in 0.001s

OK
```
- All tests passed successfully
- Execution time: 0.001 seconds
- Each test includes detailed logging of validation results

### Quality Scoring System
- Perfect valid data scores 100%
- Invalid entries score 90%
- Each validation failure is logged with specific error message
- Test results include validation details for debugging

## Progress Files

During scraper execution, files with the format `progress_batch_X.csv` are automatically generated in the `progress/` directory. These files are essential for the following reasons:

### Why are they generated?
- **Failure Recovery**: If the script is interrupted (due to network errors, system failures, etc.), progress is not lost
- **Batch Processing**: Data is saved every 10 schools processed
- **Real-time Monitoring**: Allows data quality verification during execution

### When are they generated?
1. Automatically every 10 schools processed (`progress_batch_X.csv`)
2. When an error occurs during processing (`error_recovery_X.csv`)
3. Upon completion of the entire process (`schools_data_TIMESTAMP.csv` in the `output/` directory)

### Filename Structure
- `progress_batch_X`: where X is the number of schools processed up to that point
- Includes timestamp to prevent overwrites: `progress_batch_X_YYYYMMDD_HHMMSS.csv`

### Important Note
These files are included in `.gitignore` to prevent sensitive data from being uploaded to the repository.