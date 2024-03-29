from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import configparser

import numpy as np

import re

from dateutil.parser import *
import dateutil.utils
from dateutil.relativedelta import relativedelta

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker

import os

from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from scraper import pcsparser

import scipy.stats

#Cleans the ebay formatting to retrieve the float value of the listed price
def clean_prices(text):
    new_text = text
    new_text = re.sub("[^.0-9]", '', new_text)
    return new_text

#Cleans the date formatting off of the ebay listing to retrieve the date value
def clean_dates(text):
    new_text = text
    new_text = re.sub("Sold ", '', new_text)
    return new_text

def main():
    driver = webdriver.Chrome()

    config = configparser.ConfigParser()
    cfg = config.read("config.ini")
    sections = config.sections()

    excluded = config['EXCLUDE']['Excluded']
    excluded_arr = excluded.replace(" ", "").split(",")
    exclude = "-" + "+-".join(excluded_arr)

    included = config['INCLUDE']['Included']
    included_arr = included.replace(" ", "").split(",")

    keyword = config['SEARCH']['Keyword']

    include = "\"%s\"" % keyword + "+" + "+".join(included_arr)

    page = 1
    url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=%s+%s&_sacat=0&LH_TitleDesc=0&LH_PrefLoc=1&_fsrp=1&_sop=13&LH_Complete=1&LH_Sold=1&_ipg=200&_pgn=%d" % (include, exclude, page)

    #true to retrieve every listing, but scraping that takes so so so long
    nolimit = config['SEARCH']['NoLimit'] == "True"

    #time back in history to search, in days
    timeinterval = config['SEARCH']['SearchInterval']

    today = dateutil.utils.today().date()

    earliestdate = today + relativedelta(days=-int(timeinterval))

    #output path, according to keyword ex: n95, n99, etc.
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    outputdir = os.path.join(ROOT_DIR, "../listings/%s" % keyword)
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    driver.get(url)

    titles = []
    dates = []
    prices = []
    pieces = []
    pricesppcs = []

    nextpagepath = "//a[@class='pagination__next']"
    proceed = True
    searches = 0
    while(proceed):
        i = 1
        for i in range(1, 201):
            titlepath = "//div[@id='mainContent']/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]/a/h3" % i
            pricepath = "//div[@id='mainContent']/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@class='POSITIVE' or @class='STRIKETHROUGH POSITIVE']" % i
            shippingpath = "//div[@id='mainContent']/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@class='s-item__shipping s-item__logisticsCost']" % i
            datepath = "//div[@id='mainContent']/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@role='text']" % i

            try:
                title = driver.find_element_by_xpath(titlepath).text
                price = driver.find_element_by_xpath(pricepath).text
                shipping = driver.find_element_by_xpath(shippingpath).text
                date = parse(clean_dates(driver.find_element_by_xpath(datepath).text)).date()
            except NoSuchElementException:
                print("Search terminated. " + keyword.upper() + " page " + str(page) + " had only " + str(i) + " results.")
                proceed = False
                break

            if nolimit or date >= earliestdate:
                if "Free" in shipping:
                    shipping = 0
                else:
                    shipping = float(clean_prices(shipping))

                #print(title)
                pcs = pcsparser.parse(title)

                price = float(clean_prices(price))

                prices.append(price + shipping)
                titles.append(title)
                dates.append(date)
                pieces.append(pcs)
                pricesppcs.append(price/pcs)
            else:
                searches += i
                print("End of time interval reached: " + str(searches) + " items processed.")
                proceed = False
                break
        searches += 200
        try:
            nextbutton = driver.find_element_by_xpath(nextpagepath)
            nextbutton.send_keys(Keys.RETURN)
            element_present = expected_conditions.presence_of_element_located((By.CLASS_NAME, 'POSITIVE'))
            WebDriverWait(driver, timeout = 8).until(element_present)
            page += 1
        except NoSuchElementException:
            break

    listings = {"title" : titles, "price" : prices, "date" : dates, "pcs" : pieces, "unit_price" : pricesppcs}
    listingsframe = pd.DataFrame(listings)
    table = listingsframe.to_html(os.path.join(outputdir, keyword + " chart.html"))
    print(listingsframe)
    #eliminate outliers
    z_scores = scipy.stats.zscore(listingsframe['unit_price'])
    z_scores = np.abs(z_scores)
    listingsframe['z_score'] = z_scores
    cleanframe = listingsframe[listingsframe.z_score < 3]
    cleantable = cleanframe.to_html(os.path.join(outputdir, keyword + " cleanchart.html"))

    #boxplot pyplot code
    bp = pd.DataFrame(cleanframe['unit_price']).plot.box(sym = '')
    f1 = plt.figure(1)
    plt.title(keyword.upper() + ' Price Distribution from ' + str(earliestdate) + " to " + str(today))
    f1.set_figheight(10.8)
    f1.set_figwidth(19.2)
    bp.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5))
    bp.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))
    bp.grid(b = True, which = 'both', axis = 'y')
    bp.figure.savefig(os.path.join(outputdir, keyword + " boxplot"))

    #rolling average
    days = config['SEARCH']['AveragingWindow']
    f2 = plt.figure(figsize = (19.2, 10.8))
    plt.title(keyword.upper() + " " + days + ' Day Rolling Average')
    upc = cleanframe[['date', 'unit_price']]
    mean = upc.groupby('date').mean()
    rmean = mean.unit_price.rolling(window = int(days)).mean()

    plt.plot(rmean, label = '%s Day Rolling Average' % days, color = 'blue')
    f2.savefig(os.path.join(outputdir, keyword + " rollingaverage"))

    showGraphs = bool(config['SEARCH']['ShowGraphs'])
    if(showGraphs):
        f1.show()
        f2.show()

    print("Press any key to exit.")
    input()
    driver.close()
    plt.close('all')

#TO DO
#fill in holes in dates with null values, let mean() function ignore and re-average

if __name__ == "__main__":
    main()