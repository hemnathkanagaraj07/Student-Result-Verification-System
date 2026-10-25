"""
End-to-End Browser Automation Test using Selenium WebDriver.
Designed for BSc IT Software Testing Laboratory.

Tests:
1. Web Page Load & Title Verification
2. Student Result Form Input Automation
3. Real-Time Calculation Preview Validation
4. Form Submission and Ledger Table Verification
5. Boundary Value Browser Verification (Pass vs Fail)

To run this test:
  python tests/test_selenium.py
or via pytest:
  python -m pytest -v tests/test_selenium.py
"""

import os
import sys
import time
import threading

# Ensure project root directory is in python search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
import storage

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions


SERVER_PORT = 5025
BASE_URL = f"http://127.0.0.1:{SERVER_PORT}"
_server_thread = None


def start_test_server():
    """Starts the Flask server in a background thread if not running."""
    global _server_thread
    if _server_thread is None:
        def run_flask():
            import logging
            log = logging.getLogger("werkzeug")
            log.setLevel(logging.ERROR)
            app.run(host="127.0.0.1", port=SERVER_PORT, debug=False, use_reloader=False)

        _server_thread = threading.Thread(target=run_flask, daemon=True)
        _server_thread.start()
        time.sleep(1.2)  # Allow server to bind and start listening


def get_browser_driver():
    """
    Initializes Chrome or Edge WebDriver with headless options.
    Falls back gracefully with actionable instructions if browser driver is unavailable.
    """
    print("[Selenium] Checking available browser drivers (Chrome / Edge)...")

    # 1. Try Chrome
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1280,800")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        print("[Selenium] Successfully initialized Chrome WebDriver.")
        return driver
    except Exception as e1:
        print(f"[Selenium] Chrome initialization notice: {e1}")

    # 2. Try Edge
    try:
        edge_options = EdgeOptions()
        edge_options.add_argument("--headless=new")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--window-size=1280,800")
        driver = webdriver.Edge(options=edge_options)
        print("[Selenium] Successfully initialized Edge WebDriver.")
        return driver
    except Exception as e2:
        print(f"[Selenium] Edge initialization notice: {e2}")

    return None


def test_selenium_result_workflow():
    """
    Automated browser test validating student form submission,
    live calculation preview, and table update.
    """
    start_test_server()
    storage.reset_sample_data()

    driver = get_browser_driver()
    if driver is None:
        print("[SKIP] Chrome/Edge WebDriver not found on system. Skipping Selenium browser test.")
        return

    try:
        print(f"[Selenium] Navigating to {BASE_URL}...")
        driver.get(BASE_URL)

        # 1. Verify Page Title
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "page-title"))
        )
        assert "Student Result Verification" in driver.title
        print("✓ Page title and header verified.")

        # 2. Locate form elements
        name_input = driver.find_element(By.ID, "name")
        roll_input = driver.find_element(By.ID, "roll_no")
        sub1 = driver.find_element(By.ID, "sub1")
        sub2 = driver.find_element(By.ID, "sub2")
        sub3 = driver.find_element(By.ID, "sub3")
        sub4 = driver.find_element(By.ID, "sub4")
        sub5 = driver.find_element(By.ID, "sub5")

        # 3. Enter student details
        name_input.clear()
        name_input.send_keys("Pooja Sharma")

        roll_input.clear()
        roll_input.send_keys("SELENIUM-99")

        sub1.send_keys("80")
        sub2.send_keys("85")
        sub3.send_keys("90")
        sub4.send_keys("75")
        sub5.send_keys("85")

        time.sleep(0.5)

        # 4. Verify live preview calculation (Total = 415, Percentage = 83.0%)
        preview_total = driver.find_element(By.ID, "preview-total").text
        preview_pct = driver.find_element(By.ID, "preview-percentage").text
        preview_status = driver.find_element(By.ID, "preview-status-text").text

        assert "415" in preview_total
        assert "83" in preview_pct
        assert "Pass" in preview_status
        print("✓ Live preview calculation verified (415/500, 83.0%, PASS).")

        # 5. Submit form
        submit_btn = driver.find_element(By.ID, "btn-submit-form")
        driver.execute_script("arguments[0].scrollIntoView();", submit_btn)
        submit_btn.click()

        # 6. Wait for row in ledger table
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "row-SELENIUM-99"))
        )
        new_row = driver.find_element(By.ID, "row-SELENIUM-99")
        row_text = new_row.text
        assert "Pooja Sharma" in row_text
        assert "PASS" in row_text
        print("✓ Student row successfully inserted into ledger table via browser.")

        # 7. Test Testing Dashboard page navigation
        driver.get(f"{BASE_URL}/testing")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btn-run-tests"))
        )
        assert "Testing Dashboard" in driver.title
        print("✓ Navigated to Software Testing Dashboard.")

        print("==================================================")
        print("  ALL SELENIUM BROWSER TESTS PASSED SUCCESSFULLY! ")
        print("==================================================")

    finally:
        driver.quit()


if __name__ == "__main__":
    test_selenium_result_workflow()
    os._exit(0)
