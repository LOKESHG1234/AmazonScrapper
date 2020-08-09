from amazon_config import(
    get_web_driver_options,
    get_Chrome_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    CURRENCY,
    BASE_URL,
    DIRECTORY,
)
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep as Sleep
import json
from datetime import datetime
class GenerateReport:
    def __init__(self, file_name, filters, base_link, currency, data):
        self.data = data
        self.file_name = file_name
        self.filters = filters
        self.base_link = base_link
        self.currency = currency
        reports = {
            'title': self.file_name,
            'date': self.get_now(),
            'best_item': self.get_best_item(),
            'currency': self.currency,
            'filters': self.filters,
            'base_link': self.base_link,
            'products': self.data
        }
        print("Creating report")
        with open(f'{DIRECTORY}/{file_name}.json','w') as f:
            json.dump(reports, f)
        print("Done")
    def get_now(self):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")
    def get_best_item(self):
        try:
            return sorted(self.data, key=lambda k: k['price'])[0]
        except Exception:
            print("Problem With Sorting item")
            return None

class AmazonAPI:
    def __init__(self, filters , search_term, base_url, currency):
        self.base_url = base_url
        self.search_term = search_term
        options  = get_web_driver_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver = get_Chrome_driver(options)
        self.currency = currency
        self.price_filters = f"&rh=p_36%3A{filters['min']}00-{filters['max']}00&qid=1596910428&rnid=1741393031"
    
    def run(self):
        print("Starting Script....")
        print(f"Looking for {self.search_term} products...")
        links = self.get_product_links()
        Sleep(1)
        if not links:
            print("Stopped Script...")
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products....")
        products = self.get_products_info(links)
        print(f"Got info of {len(products)} products...")
        self.driver.quit()
        return products
    
    def get_products_info(self,links):
        asins = self.get_asins(links)
        products = []
        for asin in asins:
            product = self.get_single_product_info(asin)
            if product:
                products.append(product)
        return products
    
    def get_single_product_info(self, prod_id):
        print(f'Product ID:{prod_id} - getting data...')
        product_short_url = self.short_urls(prod_id)
        self.driver.get(f'{product_short_url}?language=en_IN')
        Sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        if title and seller and price:
            product_info = {
                'asin' : prod_id,
                'url' : product_short_url,
                'title' : title,
                'seller' : seller,
                'price' : price
            }
            return product_info
        return None 

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f"Can't get title of product - {self.driver.current_url}")
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id("bylineInfo").text
        except Exception as e:
            print(e)
            print(f"Can't get Seller of product - {self.driver.current_url}")
            return None

    def get_price(self):
            # subtitle = ['Paperback' , 'Kindle' , 'Hardcover']
            price = None
            try:
                price = self.driver.find_element_by_id('priceblock_ourprice').text
                # price = self.convert_price(price)
                if price:
                    self.convert_price(price)
                else:
                    price = self.driver.find_element_by_id('priceblock_dealprice').text
                    self.convert_price(price)
                    
            except NoSuchElementException:
                try:
                    availability = self.driver.find_element_by_id('availability').text
                    if 'Available' in availability:
                        price = self.driver.find_element_by_class_name('olp-padding-right').text
                        price = price[price.find(self.currency):]
                        price = self.convert_price(price)
                except Exception as e:
                    # print(e)
                    print(f"Can't get price of a product - {self.driver.current_url}")
                    return None
            except Exception as e:
                # print(e)
                print(f"Can't get price of a product - {self.driver.current_url}")
                return None
            return price
    def convert_price(self, price):
        price = price.split(" ")[-1]
        try:
            price = price.split("\n")[0] + "." + price.split("\n")[1]
        except:
            Exception()
        try:
            price = price.split(",")[0] + price.split(",")[1]
        except:
            Exception()
        return float(price)

    def short_urls(self, prod_id):
        return self.base_url + '/dp/' + prod_id

    def get_asins(self,links):
        return [self.get_asin(link) for link in links]

    def get_asin(self,product_link):
        return(product_link[product_link.find("/dp/") + 4:product_link.find("/ref")])

    def get_product_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.search_term)
        element.send_keys(Keys.ENTER)
        Sleep(2) # wait to load page
        self.driver.get(f'{self.driver.current_url}{self.price_filters}')
        Sleep(2)
        result_list = self.driver.find_elements_by_class_name('s-result-list')
        links = []
        try:
            results = result_list[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute('href') for link in results]
            return links
        except Exception as e:
            print("Didn't get any products....")
            print(e)
            return links

if __name__ == "__main__":
    print("HEY!!!")
    NAME = input("Enter Product Name: ")
    MIN_PRICE = int(input("Enter Min Price: "))
    MAX_PRICE = int(input("Enter Max Price: "))
    FILTERS = {
        'min' : MIN_PRICE,
        'max' : MAX_PRICE
    }
    amazon = AmazonAPI(FILTERS,NAME,BASE_URL,CURRENCY)
    data = amazon.run()
    GenerateReport(NAME,FILTERS,BASE_URL,CURRENCY,data)