

from selenium import webdriver

driver=webdriver.Chrome(executable_path=r'C:\Utility\BrowserDrivers\chromedriver.exe')
driver.get("http://www.google.com")
performance_data = driver.execute_script("return window.performance.getEntries();")
print (performance_data)

