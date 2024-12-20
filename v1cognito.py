import os
import json
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ----------------------- Configuration ----------------------- #

# API Configuration
API_KEY = input("🔑 Please enter your Cognito Forms API key: ").strip()
BASE_API_URL = "https://www.cognitoforms.com/api/"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Selenium Configuration
PAGE_LOAD_TIMEOUT = 60  # Seconds
ELEMENT_LOAD_TIMEOUT = 60  # Seconds

# ----------------------- Chrome Profile Configuration ----------------------- #

# Auto-detect current username and confirm/change
default_username = os.getlogin()
CHROME_USER_NAME = input(f"🔑 Detected username '{default_username}'. Press Enter to use it or enter a different username: ").strip() or default_username
CHROME_USER_DATA_DIR = rf"C:\Users\{CHROME_USER_NAME}\AppData\Local\Google\Chrome\User Data"

# Prompt for Chrome profile directory
CHROME_PROFILE_DIR = input("Enter the Chrome profile directory (e.g., 'Default'): ").strip()

# Prompt for base path
COGNITO_BASE_PATH = input("Enter the base path for Cognito Forms: ").strip()

# ----------------------------------------------------------------- #

def initialize_driver():
    """Sets up the Selenium WebDriver with Chrome using existing profile."""
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
    chrome_options.add_argument(f"profile-directory={CHROME_PROFILE_DIR}")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress Selenium logs

    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        print("✅ WebDriver initialized successfully.")
        return driver
    except Exception as e:
        print(f"❌ Failed to initialize WebDriver: {e}")
        raise

def wait_for_manual_login(driver):
    """Wait for the user to log in manually."""
    url = f"https://www.cognitoforms.com/{COGNITO_BASE_PATH}/"
    print(f"🔗 Opening base URL: {url}")
    driver.get(url)

    print("🔒 Please log in manually in the opened Chrome browser.")
    print("When done, return to this terminal and press 'Y' to continue.")
    while True:
        user_input = input("Press 'Y' to continue: ").strip().lower()
        if user_input == 'y':
            print("✅ Proceeding with the script.")
            break
        else:
            print("⚠️ Invalid input. Press 'Y' to continue.")

def list_forms(driver):
    """Fetches all forms using Selenium and filters only those with entries."""
    forms = []
    url = f"https://www.cognitoforms.com/{COGNITO_BASE_PATH}/"
    try:
        driver.get(url)

        # Wait for page to load and ensure forms are visible
        wait = WebDriverWait(driver, ELEMENT_LOAD_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/'] span.total-entries")))

        time.sleep(5)  # Wait for forms to load completely

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        anchor_tags = soup.find_all("a", href=True)
        for a_tag in anchor_tags:
            total_entries_span = a_tag.find("span", class_="total-entries")
            if total_entries_span:
                try:
                    total_entries = int(total_entries_span.get_text(strip=True))
                except ValueError:
                    print("⚠️ Unable to parse total entries for a form. Skipping.")
                    continue

                if total_entries > 0:
                    href = a_tag['href']
                    parts = href.strip('/').split('/')
                    if len(parts) >= 2:
                        internal_name = parts[1]
                        forms.append({
                            "InternalName": internal_name,
                            "EntriesURL": f"https://www.cognitoforms.com{href}/1-all-entries",
                            "TotalEntries": total_entries
                        })
                        print(f"📋 Found Form: Internal Name='{internal_name}' with {total_entries} entries.")
        if not forms:
            print("❌ No forms with entries found.")
        return forms

    except Exception as e:
        print(f"❌ Exception while listing forms via Selenium: {e}")
        return []

def scrape_entries(driver, internal_name):
    """Scrapes entries from a form using Selenium."""
    entries = []
    url = f"https://www.cognitoforms.com/{COGNITO_BASE_PATH}/{internal_name}/entries/1-all-entries"
    print(f"\n🔗 Navigating to Entries URL: {url}")

    try:
        driver.get(url)

        # Wait until entries table is loaded
        wait = WebDriverWait(driver, ELEMENT_LOAD_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.slick-cell.l1.r1.c-id")))

        time.sleep(3)  # Wait for entries to load

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Scrape entry IDs
        for div in soup.find_all("div", class_="slick-cell l1 r1 c-id"):
            entry_id = div.get_text(strip=True)
            if entry_id:
                entries.append(entry_id)

        if not entries:
            print(f"❌ No entries found for Form '{internal_name}'.")
        else:
            print(f"✅ Found {len(entries)} entries for Form '{internal_name}'.")

        return entries

    except Exception as e:
        print(f"❌ An error occurred while scraping entries for Form '{internal_name}': {e}")
        return entries

def delete_entry(form_id, entry_id, dry_run=False):
    """Deletes an entry using the API, or simulates deletion in dry-run mode."""
    if dry_run:
        print(f"[DRY RUN] 🗑️ Would delete Entry ID {entry_id} from Form ID {form_id}.")
        return

    url = f"{BASE_API_URL}/forms/{form_id}/entries/{entry_id}"
    try:
        response = requests.delete(url, headers=HEADERS)
        if response.status_code == 204:
            print(f"✅ Successfully deleted Entry ID {entry_id} from Form ID {form_id}.")
        else:
            print(f"❌ Error deleting Entry ID {entry_id}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception while deleting Entry ID {entry_id}: {e}")

def get_form_id(internal_name):
    """Retrieves the form ID using the internal name via the API."""
    url = f"{BASE_API_URL}/forms"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            forms = response.json()
            for form in forms:
                if form.get('InternalName', '').lower() == internal_name.lower():
                    return form.get('Id')
            print(f"❌ Form with Internal Name '{internal_name}' not found via API.")
            return None
        else:
            print(f"❌ Error fetching forms to retrieve Form ID: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Exception while retrieving Form ID for '{internal_name}': {e}")
        return None

def main():
    """Main function to process forms and scrape entries."""
    print("🚀 Starting the Cognito Forms Scraper...")

    try:
        driver = initialize_driver()
    except Exception as e:
        print("❌ Failed to initialize WebDriver.")
        return

    wait_for_manual_login(driver)

    try:
        # Step 1: Fetch forms with entries
        forms = list_forms(driver)
        if not forms:
            print("❌ No forms with entries available. Exiting...")
            return

        # Step 2: Scrape entries for each form and simulate deletion
        for form in forms:
            internal_name = form['InternalName']
            print(f"\n📄 Processing Form: '{internal_name}'")

            while True:
                entries = scrape_entries(driver, internal_name)
                if entries:
                    form_id = get_form_id(internal_name)
                    if form_id:
                        # Process deletion of the entries
                        for entry_id in entries:
                            delete_entry(form_id, entry_id, dry_run=False)  # Set dry_run=False to perform actual deletion

                        # Check if we got 25 entries, and if so, refresh and scrape again
                        if len(entries) == 25:
                            driver.refresh()  # Refresh the page to continue deleting if more entries are present
                            print(f"🔄 Page refreshed. Found 25 entries, checking for more...")
                        else:
                            print(f"✅ Found fewer than 25 entries, stopping the recheck.")
                            break  # Exit the loop if fewer than 25 entries were found
                    else:
                        print(f"❌ Could not retrieve Form ID for '{internal_name}'. Entries will not be deleted.")
                else:
                    print(f"❌ No entries to delete for Form '{internal_name}'.")
                    break

    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        driver.quit()
        print("🛑 WebDriver closed.")
        print("✅ Script execution completed.")

if __name__ == "__main__":
    main()
