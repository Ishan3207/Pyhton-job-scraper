import time
import csv
import math
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_user_inputs():
    """Asks the user for search specifications."""
    print("--- Internship Scraper 3000 ---")
    job_role = input("Enter the internship role (e.g., Python Developer): ")
    location = input("Enter the location (e.g., Remote, New York, India): ")
    
    # NEW: Ask for the number of jobs
    while True:
        try:
            num_jobs = int(input("How many jobs do you want to extract? (e.g., 20): "))
            break
        except ValueError:
            print("Please enter a valid number.")
            
    return job_role, location, num_jobs

def setup_driver():
    """Sets up the automated browser."""
    service = Service(ChromeDriverManager().install())
    
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment to run invisibly
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_linkedin(job_role, location, num_jobs):
    """The main logic to go to LinkedIn and get data."""
    driver = setup_driver()
    
    base_url = f"https://www.linkedin.com/jobs/search?keywords={job_role}&location={location}"
    
    print(f"\nNavigating to: {base_url}")
    driver.get(base_url)
    time.sleep(3)
    
    # NEW: Calculate how many times to scroll based on the number of jobs you want
    # LinkedIn loads about 25 jobs per 'scroll'. We add a buffer to be safe.
    scrolls_needed = math.ceil(num_jobs / 20) + 2
    
    print(f"Scrolling {scrolls_needed} times to load enough jobs...")
    
    for _ in range(scrolls_needed):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(2) # Wait for new jobs to load

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    job_cards = soup.find_all('div', class_='base-card')
    print(f"\nFound {len(job_cards)} available jobs. Processing the first {num_jobs}...")
    
    results = []
    
    for card in job_cards:
        # NEW: Stop the loop immediately if we have enough jobs
        if len(results) >= num_jobs:
            break
            
        try:
            title_tag = card.find('h3', class_='base-search-card__title')
            title = title_tag.text.strip() if title_tag else "N/A"
            
            company_tag = card.find('h4', class_='base-search-card__subtitle')
            company = company_tag.text.strip() if company_tag else "N/A"
            
            loc_tag = card.find('span', class_='job-search-card__location')
            loc = loc_tag.text.strip() if loc_tag else "N/A"
            
            link_tag = card.find('a', class_='base-card__full-link')
            link = link_tag['href'] if link_tag else "N/A"
            
            results.append({
                "Role": title,
                "Company": company,
                "Location": loc,
                "Link": link
            })
        except Exception:
            continue
            
    driver.quit()
    return results

def save_data(data):
    """Saves the extracted data to files."""
    if not data:
        print("No jobs found to save.")
        return

    # Save to TXT
    with open("internships.txt", "w", encoding="utf-8") as f:
        for job in data:
            f.write(f"Role: {job['Role']}\n")
            f.write(f"Company: {job['Company']}\n")
            f.write(f"Location: {job['Location']}\n")
            f.write(f"Apply Here: {job['Link']}\n")
            f.write("-" * 30 + "\n")
    
    print("Saved to internships.txt!")

    # Save to CSV
    with open("internships.csv", "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Role", "Company", "Location", "Link"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print("Saved to internships.csv!")

if __name__ == "__main__":
    # NEW: We now unpack 3 variables instead of 2
    role, loc, count = get_user_inputs()
    scraped_data = scrape_linkedin(role, loc, count)
    save_data(scraped_data)