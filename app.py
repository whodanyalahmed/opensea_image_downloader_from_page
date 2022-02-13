import os
import requests
import shutil
import time
import datetime
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
driver = chrome(True)

logFile = open("log.txt", "a+")
# another log file to tractk   downloaded images
DownloadslogFile = open("downloads.txt", "a+")
logFile.write("Started at: " + str(datetime.datetime.now())+"\n")
driver.get('https://opensea.io/collection/clonex')
# This function iteratively clicks on the "Next" button at the bottom right of the search page.
image_srcs = []


def scroll_down_page_and_get_images(speed=8, num_of_nfts=10):

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
        images = soup.find_all(
            'img', src=lambda x: x and x.startswith('https://lh3'))
        # get the list of all src of images
        global image_srcs
        # remove the once available in log file

        temp = [img['src'] for img in images]

        # remove the once which are already downloaded from downloads.txt

        no_urls = ["https://lh3.googleusercontent.com/XN0XuD8Uh3jyRWNtPTFeXJg_ht8m5ofDx6aHklOiy4amhFuWUa0JaR6It49AH8tlnYS386Q0TW_-Lmedn0UET_ko1a3CbJGeu5iHMg=s130",
                   "https://lh3.googleusercontent.com/4elUtz8UyFYDH34vDxd4hpQX8S-EdkFq8s9ombkuQTDBWLwHvsjRM_RXWT2zX8Vt2bAiO2BHslwN57FyTW1JIn_FyFI0BsZfmvmeJQ=h600"]
        for image_src in temp:
            if os.path.basename(image_src) in open("downloads.txt").read() or image_src in no_urls:
                # print(len(temp))
                temp.remove(image_src)
                # print("removed: ", image_src)
                # print(len(temp))
        image_srcs.extend(temp)
        # Remove the below link

        for image_src in image_srcs:
            if os.path.basename(image_src) in open("downloads.txt").read() or image_src in no_urls:
                # print(len(image_srcs))
                image_srcs.remove(image_src)
                # print("removed: ", image_src)
                # print(len(image_srcs))

        # added temp to image_srcs
        # remove duplicates
        image_srcs = list(set(image_srcs))
        # print(len(image_srcs))
        print("info: searching.....")
        # check length of image_srcs is equal to num_of_nfts
        if len(image_srcs) >= num_of_nfts:
            break


# scroll_down_page(10)
driver.implicitly_wait(10)
scroll_down_page_and_get_images(150, num_of_nfts=num_of_nfts)
print("successfully completed the page scrolling")
logFile.write("successfully completed the page scrolling"+"\n")

# download images from image_srcs using requests
for image_src in image_srcs[:num_of_nfts]:
    # print(image_src)
    # skip the image if it is already present in the logfile
    if os.path.basename(image_src) in open("downloads.txt").read():
        print("skipping image: " + image_src)
        logFile.write("skipping image: " + image_src+"\n")
        continue
    print("info : Downloading image: " + image_src)
    # save image to local directory
    response = requests.get(image_src, stream=True)
    # check if path exists if doesnt create it
    if not os.path.exists('images'):
        os.mkdir('images')
    # save image to local directory

    with open(os.getcwd()+"\\images\\"+os.path.basename(image_src)+".png", 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
        logFile.write(os.path.basename(image_src)+".png"+"\n")
        DownloadslogFile.write(os.path.basename(image_src)+".png"+"\n")

    del response
    time.sleep(1)
logFile.close()
DownloadslogFile.close()
# close the driver and free the memory
driver.quit()
print("successfully completed the downloads")
