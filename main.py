from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from numpy import mean, median, percentile
import numpy as np

import re

from dateutil.parser import *
from dateutil.utils import today
from dateutil.relativedelta import relativedelta
from datetime import *

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker

import os

def clean_prices(text):
    new_text = text
    new_text = re.sub("[^.0-9]", '', new_text)
    return new_text

def clean_dates(text):
    new_text = text
    new_text = re.sub("Sold ", '', new_text)
    return new_text

def clean_pcs(text):
    empty = []
    if " " in text:
        text_array = text.split(" ")
        for x in range(len(text_array) -1, -1, -1):
            text_array[x] = re.sub("[^/0-9]", '', text_array[x])
            if text_array[x] == "":
                text_array.pop(x)
        try:
            pcsstring = text_array[len(text_array) - 1]
        except IndexError:
            return 1
    else:
        pcsstring = re.sub("[^/0-9]", '', text)
        if pcsstring == "":
            return 1
    if "/" in pcsstring:
        pieces = pcsstring.split("/")
        pcs = pieces[0]
    else:
        if pcsstring != " ":
            pcs = pcsstring
        else:
            return 1
    return pcs

driver = webdriver.Chrome("C:/Users/nytig/seleniumchrome/chromedriver.exe")

excludes = open("excludes", "r")
excluded = excludes.readlines()
for i in range(0, len(excluded)):
    excluded[i] = excluded[i].replace("\n", "")

includes = open("includes", "r")
included = includes.readlines()
for i in range(0, len(included)):
    included[i] = included[i].replace("\n", "")

exclude = "-" + "+-".join(excluded)
keyword = included[0]
included.pop(0)

include = "\"%s\"" % keyword + "+" + "+".join(included)

timeinterval = ""
today = today().date()

if timeinterval == "":
    earliestdate = today + relativedelta(months=-1)
else:
    earliestdate = today + relativedelta(days=-int(timeinterval))

page = 1
url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=%s+%s&_sacat=0&LH_TitleDesc=0&LH_PrefLoc=1&_fsrp=1&_sop=13&LH_Complete=1&LH_Sold=1&_ipg=200&_pgn=%d" % (include, exclude, page)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
outputdir = os.path.join(ROOT_DIR, "listings/%s" % keyword)
if not os.path.exists(outputdir):
    os.makedirs(outputdir)

driver.get(url)

titles = []
dates = []
prices = []
pieces = []

for i in range(1, 201):
    titlepath = "/html/body/div[4]/div[4]/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]/a/h3" % i
    pricepath = "/html/body/div[4]/div[4]/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@class='POSITIVE' or @class='STRIKETHROUGH POSITIVE']" % i
    shippingpath = "/html/body/div[4]/div[4]/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@class='s-item__shipping s-item__logisticsCost']" % i
    datepath = "/html/body/div[4]/div[4]/div[2]/div[1]/div[2]/ul/li[%d]/div/div[2]//span[@role='text']" % i

    try:
        title = driver.find_element_by_xpath(titlepath).text
        price = driver.find_element_by_xpath(pricepath).text
        shipping = driver.find_element_by_xpath(shippingpath).text
        date = parse(clean_dates(driver.find_element_by_xpath(datepath).text)).date()
    except NoSuchElementException:
        print("Search terminated. " + keyword.upper() + " page " + str(page) + " had only " + str(i) + " results.")
        break

    if date >= earliestdate:
        if "Free" in shipping:
            shipping = 0
        else:
            shipping = float(clean_prices(shipping))

        index = -1
        uppertitle = title.upper()
        if "PCS" in uppertitle:
            index = uppertitle.find("PCS")
        elif "PACK" in uppertitle:
            index = uppertitle.find("PACK")
        elif "PC" in uppertitle:
            index = uppertitle.find("PC")
        elif "PK" in uppertitle:
            index = uppertitle.find("PK")
        elif "QTY" in uppertitle:
            index = uppertitle.find("QTY")

        if index == -1:
            pcs = 1
        else:
            pcs = clean_pcs(title[0:index].strip())

        price = float(clean_prices(price))

        prices.append(price + shipping)
        titles.append(title)
        dates.append(date)
        pieces.append(pcs)
    else:
        print("End of time interval reached: " + str(i) + " items processed.")
        break

listings = {"titles" : titles, "prices" : prices, "dates" : dates, "pcs" : pieces}
listingsframe = pd.DataFrame(listings)
table = listingsframe.to_html()
tableout = open(os.path.join(outputdir, keyword + " chart"), "wt")
tableout.write(table)
tableout.close()
print(listingsframe)

# listings = {"titles" : titles, "prices" : prices, "dates" : dates}
# listingframe = pd.DataFrame(listings)
#
# print(name.upper() + ":")
# print("$" + str(round(mean(prices), 2)) + " Mean")
# print("$" + str(round(median(prices), 2)) + " Median")
# print("$" + str(round(percentile(prices, 25), 2)) + " 25th Percentile")
# print("$" + str(round(percentile(prices, 75), 2)) + " 75th Percentile")
# print(listingframe[['prices', 'dates']])
#
# #boxplot pyplot code
# bp = pd.DataFrame(listingframe['prices']).plot.box()
# plt.figure(1)
# plt.title(name.upper() + ' Price Distribution')
# bp.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(10))
# bp.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator(5))
# bp.grid(b = True, which = 'both', axis = 'y')
# bp.figure.savefig(os.path.join(outputdir, name + " boxplot"))
#
# #rolling average
# f2 = plt.figure(figsize = (19.2, 10.8))
# plt.title(name.upper() + ' 3 Day Rolling Average')
# pc = listingframe[['dates', 'prices']]
# mm = pc.prices.rolling(window = 3).mean()
#
# #pc = plt.plot(pc.dates, pc.prices, label = 'Average Price', color = 'blue')
# mm = plt.plot(listingframe['dates'], mm, label = '3 Day Rolling Average', color = 'blue')
# f2.savefig(os.path.join(outputdir, name + " lineplot"))

driver.close()
excludes.close()
includes.close()
#plt.close('all')

#TO DO
#Extract pack numbers
#add multi page functionality
#pk, pcs, pc, pack, qty

