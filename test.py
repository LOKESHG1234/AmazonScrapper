from amazon_config import(
    get_web_driver_options,
    get_Chrome_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    NAME,
    CURRENCY,
    BASE_URL,
    DIRECTORY
)

from selenium.webdriver.common.keys import Keys
from time import sleep as Sleep
options  = get_web_driver_options()
set_ignore_certificate_error(options)
set_browser_as_incognito(options)
driver = get_Chrome_driver(options)
driver.get(BASE_URL)
element = driver.find_element_by_id("twotabsearchtextbox")
element.send_keys(NAME)
element.send_keys(Keys.ENTER)
test = driver.find_elements_by_class_name("a-dropdown-prompt")
print(element)
print(test)