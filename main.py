from fastapi import FastAPI, Form, File, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import asyncio
import threading


app = FastAPI()

progress = {"progress": 0, "status": "Idle"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def build_driver(headless=False):
    # Enable Chrome performance logging
    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,900")

    # Merge capabilities into options (new Selenium 4+ way)
    for key, value in caps.items():
        options.set_capability(key, value)

    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )


def run_myutep_sequence(username, password):
    global progress
    driver = build_driver(headless=False)
    wait = WebDriverWait(driver, 60)

    try:
        # 🌐 1️⃣ Open MyUTEP Portal
        progress["progress"] = 5
        progress ["status"] = "Opening MyUTEP portal..."
        driver.get("https://my.utep.edu")
        print("✅ Opened MyUTEP portal")

        # 🔗 2️⃣ Click the 'Goldmine' link
        print("⏳ Waiting for Goldmine link...")
        goldmine_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Goldmine')]")))
        goldmine_link.click()
        print("✅ Clicked Goldmine link")

        # 🪟 3️⃣ Switch to the new tab
        time.sleep(3)
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            print("🪟 Switched to Goldmine tab")

        # 🔑 4️⃣ Log in with credentials
        print("⏳ Waiting for login fields...")
        user_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='text'][name*='user'], input[type='text'][id*='user']")))
        pass_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password'][name*='pass'], input[type='password'][id*='pass']")))

        user_field.send_keys(username)
        pass_field.send_keys(password)
        print("✅ Entered credentials")

        # 🖱️ Click “Sign In”
        sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign In')]")))
        sign_in_button.click()
        print("✅ Submitted credentials")

        # ⏳ 5️⃣ Wait for Duo 2FA + New Goldmine dashboard
        print("⏳ Waiting for New Goldmine page (post-2FA)...")
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'New Goldmine')]")))
        print("✅ Logged in successfully!")

        # 📋 6️⃣ Click Registration
        registration_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Registration')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", registration_link)
        time.sleep(0.5)
        registration_link.click()
        print("✅ Opened Registration page")

        # 🧾 7️⃣ Click “Register for Classes”
        register_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Register for Classes')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", register_link)
        register_link.click()
        print("✅ Navigated to Register for Classes")

        # 🕐 8️⃣ Wait for “Select a Term” page
        WebDriverWait(driver, 60).until(EC.title_contains("Select a Term"))
        print("✅ Select a Term page loaded")

        # 🎯 9️⃣ Choose first available term (Select2 dropdown)
        print("🧠 Opening term dropdown via jQuery Select2...")
        driver.execute_script("""
            if (typeof jQuery !== 'undefined' && $('#s2id_txt_term').length) {
                $('#s2id_txt_term').select2('open');
            }
        """)
        time.sleep(1)

        dropdown_active = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'select2-drop-active')]")))
        first_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'select2-drop-active')]//ul/li[1]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", first_option)
        first_option.click()
        print("✅ Selected first visible term")

        # Force-close dropdown & trigger “change” event
        driver.execute_script("""
            var termInput = $('#txt_term');
            var selectedLi = $('.select2-drop-active li:first');
            var val = selectedLi.data('select2-data')?.id || '202620';
            termInput.val(val).trigger('change');
            $('.select2-drop-active').hide();
        """)

        chosen_text = driver.execute_script("return document.querySelector('.select2-chosen')?.textContent?.trim();")
        print(f"📅 Selected term: {chosen_text}")

        # ➡️ Continue to next page
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Continue')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
        driver.execute_script("arguments[0].click();", continue_button)
        print("✅ Clicked Continue")

        # Wait for Register for Classes page to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(., 'Register for Classes')]")))
        print("✅ Register for Classes page loaded")

        # 📘 10️⃣ Fill in Subject and Course Number
        subject_name = "Physics"
        course_number = "2320"

        print(f"🔍 Searching for subject '{subject_name}'...")
        subject_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#s2id_txt_subject input.select2-input")))
        subject_input.click()
        subject_input.send_keys(subject_name)

        # Wait and select exact match
        option_xpath = f"//div[contains(@class,'select2-result-label')][normalize-space()='{subject_name}']"
        match_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        match_option.click()
        print(f"✅ Selected subject: {subject_name}")

        # Verify tag added
        WebDriverWait(driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, f"//li[contains(@class,'select2-search-choice')]/div[normalize-space()='{subject_name}']"))
        )
        print("🏷️ Verified subject tag added!")

        # Enter course number
        course_input = wait.until(EC.element_to_be_clickable((By.ID, "txt_courseNumber")))
        course_input.clear()
        course_input.send_keys(course_number)
        print(f"✅ Entered course number: {course_number}")

        # 🔎 Click Search
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Search')]")))
        driver.execute_script("arguments[0].scrollIntoView(true);", search_button)
        driver.execute_script("arguments[0].click();", search_button)
        print("✅ Clicked Search")

        # 🧩 11️⃣ Wait for results table
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, "//table[.//th[normalize-space()='Instructor']]"))
        )
        print("✅ Search results table detected")

        # 🧾 12️⃣ Extract instructors across pages
        print("🔁 Extracting instructors from all result pages...")
        instructors = set()

        while True:
            table = driver.find_element(By.XPATH, "//table[.//th[normalize-space()='Instructor']]")
            rows = table.find_elements(By.XPATH, ".//tbody/tr")

            for r in rows:
                cells = r.find_elements(By.TAG_NAME, "td")
                if len(cells) > 7:
                    name = cells[7].text.strip()
                    if name and name.lower() not in {"tba", "staff"}:
                        instructors.add(name)

            # Look for “Next Page” button
            try:
                next_button = driver.find_element(By.XPATH, "//button[contains(@title,'Next Page') or contains(@aria-label,'Next Page')]")
            except:
                next_button = None

            if not next_button or not next_button.is_enabled():
                break

            print("➡️ Moving to next page...")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//table[.//th[normalize-space()='Instructor']]"))
            )

        instructors = sorted(instructors)
        print(f"✅ Found {len(instructors)} instructor(s):")
        progress["progress"] = 100
        progress ["status"] = "Found professors! Reloading..."
        for name in instructors:
            print(" -", name)

        print("🎉 Workflow completed successfully")
        return JSONResponse(content={"message": "Automation completed!"})

    finally:
        driver.quit()


@app.get("/progress")
async def get_progress():
    return JSONResponse(content=progress)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    print(f"📄 Uploaded file saved to {file_path}")
    # ✅ Send an actual success response
    return JSONResponse(content={"message": "File uploaded successfully"}, status_code=200)


@app.post("/run")
async def run_automation(username: str = Form(...), password: str = Form(...)):
    print(f"Running automation with {username=}")
    # 🧠 Run the automation on a separate thread
    thread = threading.Thread(target=run_myutep_sequence, args=(username, password))
    thread.start()

    return JSONResponse({"message": "Automation started"}, status_code=200)
    


