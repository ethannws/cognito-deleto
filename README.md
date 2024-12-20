# Cognito Deleto

This script allows you to scrape entries from Cognito Forms using Selenium, retrieve the form IDs, and delete entries via the Cognito Forms API. It's designed to run with a Chrome browser using a specified Chrome user profile.

## Features
- **Scrape Entries:** Scrapes form entries from Cognito Forms.
- **Delete Entries:** Deletes form entries via the Cognito Forms API.
- **Selenium Automation:** Automates browser interactions using Selenium WebDriver.
- **Manual Login:** Waits for you to manually log in to your Cognito Forms account in the browser.

## Prerequisites

1. **Python 3.x**: Ensure you have Python 3.6 or later installed.
2. **Cognito Forms API Key**: You need a Cognito Forms API key for authentication. If you don’t have one, you can request it from your Cognito Forms account.
3. **Chrome WebDriver**: The script uses Selenium WebDriver to interact with Chrome, and it automatically installs the correct driver version for your system using `webdriver-manager`.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ethannws/cognito-deleto.git
   cd cognito-deleto
Install the required Python dependencies:

bash
Copy code
pip install -r requirements.txt
The requirements.txt file includes the following packages:

selenium
beautifulsoup4
requests
webdriver-manager
Set up Chrome profile:

The script uses an existing Chrome profile for authentication. Make sure you have a valid Chrome profile set up. You can find your Chrome profile directory under C:\Users\<YourUsername>\AppData\Local\Google\Chrome\User Data.
Get your Cognito Forms API key:

Go to Cognito Forms API and retrieve your API key from the account settings.
Usage
1. Retrieve the Base URL from Cognito Forms
To obtain the base URL for a specific form:

Go to https://www.cognitoforms.com/copythis/ (replace "copythis" with your own account's base URL).
The URL for the base form page will be in the format: https://www.cognitoforms.com/<YourBasePath>.
Use this <YourBasePath> when prompted by the script.
2. Running the Script
Run the script using Python:

bash
Copy code
python cognito_forms_scraper.py
3. Walkthrough of the Script
The script will first ask for your Cognito Forms API key.
Then, it will auto-detect your Chrome username and ask you if you want to use it.
You will need to manually log in to Cognito Forms when prompted.
After login, the script will list the forms that have entries.
The script will then scrape the entries and simulate deletion (can be toggled by setting the dry_run parameter).
If there are 25 or more entries, it will refresh the page to continue processing.
Example Output:
plaintext
Copy code
🚀 Starting the Cognito Forms Scraper...
🔑 Please enter your Cognito Forms API key: <your-api-key>
🔑 Detected username 'user'. Press Enter to use it or enter a different username: 
Enter the Chrome profile directory (e.g., 'Default'): Default
Enter the base path for Cognito Forms: yourbasepath
🔗 Opening base URL: https://www.cognitoforms.com/yourbasepath/
🔒 Please log in manually in the opened Chrome browser.
When done, return to this terminal and press 'Y' to continue.
Press 'Y' to continue: y
✅ Proceeding with the script.
📋 Found Form: Internal Name='exampleForm' with 30 entries.
✅ Found 30 entries for Form 'exampleForm'.
[DRY RUN] 🗑️ Would delete Entry ID <entry_id> from Form ID <form_id>.
...
Customization
Chrome Profile Directory: You can customize the Chrome profile used by specifying the profile directory path.
Dry Run Mode: If you only want to simulate deletion without making any actual changes, set dry_run=True in the delete_entry function.
License
This project is licensed under the MIT License - see the LICENSE file for details.
