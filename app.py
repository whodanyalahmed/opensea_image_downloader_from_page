import os
import requests
import shutil
import time,datetime
from bs4 import BeautifulSoup
from selenium import webdriver

num_of_nfts = int(input("Enter number of NFTs: "))


def chrome(headless=False):
    # support to get response status and headers
    d = webdriver.DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'performance': 'ALL'}
    opt = webdriver.ChromeOptions()
    if headless:
        opt.add_argument("--headless")
    opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    opt.add_argument("--disable-popup-blocking")
    browser = webdriver.Chrome(
        executable_path=r'i://clients//chromedriver.exe', options=opt, desired_capabilities=d)
    browser.implicitly_wait(10)
    browser.maximize_window()
    return browser


# Pass True if you want to hide chrome browser
driver = chrome()

logFile = open("log.txt","a+")
logFile.write("\nStarted at: " + str(datetime.datetime.now()))
driver.get('https://opensea.io/collection/clonex')
# This function iteratively clicks on the "Next" button at the bottom right of the search page.
image_srcs = []

def scroll_down_page_and_get_images(speed=8,num_of_nfts=10):
    
    current_scroll_position, new_height = 0, 1
    while current_scroll_position <= new_height:
        current_scroll_position += speed
        driver.execute_script(
            "window.scrollTo(0, {});".format(current_scroll_position))
        new_height = driver.execute_script(
            "return document.body.scrollHeight")
        # get page source
        page_source = driver.page_source
        # parse the page source
        soup = BeautifulSoup(page_source, 'html.parser')
        # get the list of all the images with src that starts with "https://lh3"
        images = soup.find_all('img', src=lambda x: x and x.startswith('https://lh3'))
        # get the list of all src of images
        global image_srcs
        image_srcs = [img['src'] for img in images]
        # check length of image_srcs is equal to num_of_nfts
        if len(image_srcs) >= num_of_nfts:
            break
        



# scroll_down_page(10)
driver.implicitly_wait(10)
scroll_down_page_and_get_images(num_of_nfts)
print("successfully completed the page scrolling")
logFile.write("\nsuccessfully completed the page scrolling")

# download images from image_srcs using requests

for image_src in image_srcs:
    # skip the image if it is already present in the logfile
    if os.path.basename(image_src) in open("log.txt").read():
        print("skipping image: " + image_src)
        logFile.write("\nskipping image: " + image_src)
        continue
    print(image_src)
    # save image to local directory
    response = requests.get(image_src, stream=True)
    # check if path exists if doesnt create it
    if not os.path.exists('images'):
        os.mkdir('images')
    # save image to local directory

    with open(os.getcwd()+"\\images\\"+os.path.basename(image_src)+".png", 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        logFile.write("\n"+os.path.basename(image_src)+".png")

    del response
    time.sleep(1)
