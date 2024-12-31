from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyotp
import subprocess
from config import config
import time

class PortUpdater:
    def __init__(self):
        print("Initializing PortUpdater")
        chrome_options = Options()
        if config['headless']:
            print("Running headless")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        else:
            print("Running with GUI browser")
        
        # Set the binary location if specified in the config
        if 'chrome_binary_path' in config and config['chrome_binary_path']:
            chrome_options.binary_location = config['chrome_binary_path']

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        print("PortUpdater initialized")

    def login_to_windscribe(self):
        print("Logging into Windscribe")
        try:
            self.driver.get(config['windscribe']['url'])
            print("Navigated to Windscribe login page")
            # Login
            username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
            password = self.driver.find_element(By.XPATH, '//*[@id="pass"]')
            username.send_keys(config['windscribe']['username'])
            password.send_keys(config['windscribe']['password'])
            print("Entered Windscribe login credentials")
            # Handle 2FA if needed
            if '2fa_secret' in config['windscribe']:
                print("2FA secret found, handling 2FA")
                # Click on "Use 2FA?" so it can be interacted with
                element = self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/div/form/a')))
                element.click()
                print("Clicked on 2FA button")
                # Get TOTP key from config, calculate, and paste
                totp = pyotp.TOTP(config['windscribe']['2fa_secret'])
                code = self.driver.find_element(By.XPATH, '//*[@id="code"]')
                code.send_keys(totp.now())
                print("Entered 2FA code")
            password.submit()
            print("Submitted Windscribe login form")
            time.sleep(2)  # Wait for login to complete
            print("Windscribe login complete")
        except Exception as e:
            print(f"Error logging into Windscribe: {str(e)}")
            # Print the current state of the HTML page
            print("Current HTML page source:")
            print(self.driver.page_source)
            raise

    def get_port_from_windscribe(self):
        print("Getting port from Windscribe")
        try:
            # Navigate to port forward page
            self.driver.get('https://windscribe.com/myaccount#porteph')
            self.driver.refresh()
            print("Navigated to Windscribe port forward page")
            time.sleep(2)
            # Check to see if there is a port that already exists
            # If so, click the button to remove it
            delete_port_button_xpath = '//button[@class="btn green-btn" and text()="Delete Port"]'
            delete_port_button = self.driver.find_element(By.XPATH, delete_port_button_xpath)
            if delete_port_button.is_enabled():
                print("Existing port found, deleting")
                delete_port_button.click()
                print("Deleted existing port")
            # Re-locate the new port button after any potential page changes
            time.sleep(2)
            new_port_button_xpath = '/html/body/div[1]/div[3]/div/div[6]/div/div[3]/div/button[1]'
            new_port_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, new_port_button_xpath)))
            new_port_button.click()
            print("Clicked on new port button")
            # Get the port value
            time.sleep(2)
            port_element = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div[6]/div/div[3]/div/div[1]/span[2]')))
            print("Got new port value")
            return port_element.text
        except Exception as e:
            print(f"Error getting port from Windscribe: {str(e)}")
            raise

    def update_qbittorrent_port(self, port):
        print("Updating qBittorrent port")
        try:
            # Login to qBittorrent
            self.driver.get(config['qbittorrent']['url'])
            print("Navigated to qBittorrent login page")
            username = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
            password = self.driver.find_element(By.XPATH, '//*[@id="password"]')
            username.send_keys(config['qbittorrent']['username'])
            password.send_keys(config['qbittorrent']['password'])
            print("Entered qBittorrent login credentials")
            password.submit()
            print("Submitted qBittorrent login form")
            time.sleep(2)
            # Navigate to preferences
            pref_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="preferencesButton"]')))
            pref_button.click()
            print("Clicked on preferences button")
            # Click on connection link
            conn_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="PrefConnectionLink"]')))
            conn_link.click()
            print("Clicked on connection link")
            # Update port
            port_input = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="port_value"]')))
            port_input.clear()
            port_input.send_keys(port)
            print("Updated port value")
            time.sleep(1)
            print(port)
            # Save
            save_button = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[3]/div/div/div[9]/input')
            save_button.click()
            print("Clicked on save button")
            time.sleep(2)
        except Exception as e:
            print(f"Error updating qBittorrent port: {str(e)}")
            raise

    def restart_docker_container(self):
        print("Restarting Docker container")
        try:
            subprocess.run(['docker', 'restart', 'qbittorrentvpn'], check=True)
            print("Docker container restarted successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error restarting Docker container: {str(e)}")
            raise

    def run(self):
        print("Running PortUpdater")
        try:
            self.login_to_windscribe()
            port = self.get_port_from_windscribe()
            self.update_qbittorrent_port(port)
            self.restart_docker_container()
        finally:
            self.driver.quit()
            print("PortUpdater finished")

if __name__ == "__main__":
    updater = PortUpdater()
    updater.run()