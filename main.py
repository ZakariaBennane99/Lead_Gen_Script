from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
import openai
import time


def checkPerson(title):
    try:
        print("Debug: Inside checkPerson function")
        print(f"Debug: Checking title: {title}")
        
        openai.api_key = "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" # Make sure this API key is correct and valid

        print("Debug: About to make OpenAI API call")
        comp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Answer with Yes. or No. Does the following contain a real person's name: " + title}
            ],
            temperature=0
        )
        print("Debug: API call completed")

        response_content = comp.choices[0].message.content
        print(f'Debug: The return from within CheckPerson: {response_content}')
        
        return response_content
    except Exception as e:
        print("Debug: An exception occurred")
        print(e)
        traceback.print_exc()

        return "Error"




def parse_follower_count(follower_str):
    # Extract only the number and the K/M character if it exists
    match = re.search(r'([\d.]+[KkMm]?)', follower_str)
    if match:
        follower_str = match.group(1).upper()

    print(f"Debug: follower_str after regex and upper(): {follower_str}")  # Debug line

    if 'K' in follower_str:
        print("Debug: Entering 'K' condition")  # Debug line
        return int(float(follower_str.replace('K', '')) * 1000)
    elif 'M' in follower_str:
        print("Debug: Entering 'M' condition")  # Debug line
        return int(float(follower_str.replace('M', '')) * 1000000)
    else:
        print("Debug: Entering 'else' condition")  # Debug line
        return int(follower_str.replace(',', ''))


# Initialize Selenium WebDriver
driver = webdriver.Chrome()

time.sleep(1.5)

# Navigate to the login page
driver.get("https://www.pinterest.com/login")

# Refresh the page to make use of the cookies
driver.refresh()

time.sleep(2)

# Enter email and password and login
email_box = driver.find_element(By.CSS_SELECTOR, "#email")
email_box.send_keys("hello@drivendynamics.co.uk")

password_box = driver.find_element(By.CSS_SELECTOR, "#password")
password_box.send_keys("Ry6ZpEVXR=%q;wi")

login_button = driver.find_element(By.CSS_SELECTOR, "#mweb-unauth-container > div > div:nth-child(3) > div > div > div:nth-child(3) > form > div:nth-child(7) > button > div")
login_button.click()

# Allow time for login to complete
time.sleep(5)
"""
search_bar = driver.find_element(By.CSS_SELECTOR, "#searchBoxContainer > button > div > div > svg")
search_bar.click()"""

time.sleep(1)

# Type in the search bar
search_box = driver.find_element(By.CSS_SELECTOR, "#searchBoxContainer > div > div > div.ujU.zI7.iyn.Hsu > input[type=text]")
search_box.send_keys("healthy food")
search_box.send_keys(Keys.RETURN)
time.sleep(3)
profiles_icon = driver.find_element(By.CSS_SELECTOR, "#__PWS_ROOT__ > div > div:nth-child(1) > div > div.appContent > div > div > div.qiB > div > div > div > div:nth-child(2) > div > div > div > a > div > div > div > div:nth-child(2) > div")
profiles_icon.click()
time.sleep(10)


# Initialize last index to 0
last_index = 0

# Initialize profile link storage
profile_links = []

# Loop until you gather enough profiles
while len(profile_links) < 300:
    time.sleep(2)
    # Find profiles based on your provided selector
    profiles = driver.find_elements(By.CSS_SELECTOR, "#__PWS_ROOT__ > div > div:nth-child(1) > div > div.appContent > div > div > div.sLG.zI7.iyn.Hsu > div > div:nth-child(1) > div > div > div > div > div")
    # Only examine profiles from last_index to the end of the list
    for i in range(last_index, len(profiles)):
        profile = profiles[i]
        
        # Extract follower count and profile link (use appropriate selectors)  
        profile_name = profile.find_element(By.CSS_SELECTOR, "[class='tBJ dyH iFc sAJ O2T zDA IZT H2s CKL']")  # Replace with actual followers selector
        print('THE NAME', profile_name.text)
        isPerson = checkPerson(profile_name.text) 
        followers_element = profile.find_element(By.CSS_SELECTOR, "[class='tBJ dyH iFc dR0 O2T zDA IZT swG']")
        print('THE FOLLOWERS', followers_element.text)
        followers_count = parse_follower_count(followers_element.text)

        print(profile_links)
        
        if 9000 <= followers_count <= 50000 and isPerson == 'Yes.':
            profile_link = profile.find_element(By.CSS_SELECTOR, "[aria-label='profile name details']").get_attribute("href")  # Replace with actual link selector
            profile_links.append('https://www.pinterest.com' + profile_link)
        
        if len(profile_links) >= 300:
            break

    # Update last index to resume from this point after scrolling
    last_index = len(profiles)

    # Scroll down to load more profiles
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(4)

driver.quit()

print(profile_links)
