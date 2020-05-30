# PPEScraper created by Tiger Peng
[Intro and Setup]\
This app is a web scraper that scrapes Ebay's sold listings area for PPE listings, specifically masks, and allows you to see what
other people have been paying, as well as the fluctuations in the Ebay mask market! Spooky!

The "scrape.bat" file is a quickstart using default configurations, which will search ebay sold listings for n95 mask sales starting one
month ago, and display both a box and whisker and a 5 day rolling average plot for price per mask.

Note that, due to the nature of the data in certain less common mask categories like n100, rolling average plots have lots of holes and if too large an averaging window is entered, the rolling average plot may fail to show up entirely. If you predict the item you're searching is a low volume item, put a correspondingly small averaging window the config.cfg file, under "AveragingWindow."

Note:\
In order to use this application, you have to have python 3.7 installed, navigated to the project root (where requirements.txt is) and run:

pip install -r requirements.txt

In order to install the required modules.

Additionally, you will have to install the selenium driver of your respective browser here:

https://www.selenium.dev/documentation/en/webdriver/driver_requirements/

and place it in your system's PATH.


[Use]\
When you open this project, locate the file "scrape.bat", which is a quickstart for a n95 mask search as described in the intro. Additional
arguments include:\
   -u, tags the search as unlimited, meaning it will search through every listing. Takes a long long time\
   -i, tags the search to make the graphs invisible, i.e. don't display the graphs at the end.
   
   The "invisible.bat" and "unlimited.bat" have been included for you as well.
   
After you've executed the program, you'll be outputted:\
  "(keyword) chart.html", a chart of all the scraped listings in the given time frame
  "(keyword) cleanchart.html", the same chart, but with outliers removed
  "(keyword) boxplot.png", a box and whisker plot of the price distribution
  "(keyword) rollingaverage.png", a rolling average plot of the price fluctuation over the given time frame
  
  These images and files will be stored in the listings folder in the project root. They will look something like this:
  ![N95 Box and Whisker Plot](https://github.com/ThatKidTiger/PPEScraper/blob/master/examples/n95/n95%20boxplot.png)
  
Obviously, you'll want to search for more than just one type of mask, and one month in the past. For that, you'll have to go to
the config.ini file.


[Configs]

SEARCH:\
  Keyword: The specific term that distinguishes the type of mask you're looking for. Ex: Surgical, n95, n99, n100
  
  NoLimit: Changing this to True (capital T) will make the program go through every single sold listing of that product.
  If you choose this you'd better have patience.
  
  SearchInterval: Alternative to NoLimits and the default 28 day search window, this lets you customize the number of
  days back in time you would like to search for listings
  
  AveragingWindow: The number of days that the rolling average window will span. Remember, keep it low for low volume 
  products, or you might not get a graph.
  
  ShowGraphs: Whether or not you get matplotlib popups that show you the box and whisker and rolling average. Set to 
  False if you just want to have the saved images.
  
INCLUDE:\
  Included: A comma separated list (spaces are fine) of terms that will be included in the ebay search
  
EXCLUDE:\
  Excluded: A comma separated list (spaces are fine) of terms that will be specifically excluded from the search
