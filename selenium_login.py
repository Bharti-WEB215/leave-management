import os

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


APP_URL = os.environ.get("APP_URL", "http://127.0.0.1:5000")
USERNAME = os.environ.get("DEMO_USERNAME", "demo")
PASSWORD = os.environ.get("DEMO_PASSWORD", "leave123")


def verify_login_accepts_valid_credentials_and_rejects_invalid_ones():
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get(f"{APP_URL}/login")
        wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.url_contains("/dashboard"))
        assert "Employee Leave Management" in driver.page_source

        days = driver.find_element(By.NAME, "requested_days")
        reason = driver.find_element(By.NAME, "reason")
        days.send_keys("3")
        reason.send_keys("Selenium regression test")
        driver.find_element(By.CSS_SELECTOR, "#apply-form button").click()
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "message"), "Leave request submitted."
            )
        )
        assert days.get_attribute("value") == ""
        wait.until(
            EC.text_to_be_present_in_element((By.ID, "balance"), "pending: 3")
        )
        assert "Selenium regression test (pending)" in driver.find_element(
            By.ID, "requests"
        ).text

        driver.get(f"{APP_URL}/login")
        wait.until(EC.visibility_of_element_located((By.NAME, "username")))
        driver.find_element(By.NAME, "username").send_keys(USERNAME)
        driver.find_element(By.NAME, "password").send_keys("wrong-password")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[role='alert']")))
        assert "Invalid username or password" in driver.find_element(
            By.CSS_SELECTOR, "[role='alert']"
        ).text
    except TimeoutException as error:
        raise AssertionError("Login page did not reach the expected state in time") from error
    finally:
        driver.quit()


if __name__ == "__main__":
    verify_login_accepts_valid_credentials_and_rejects_invalid_ones()
