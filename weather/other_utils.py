## IMPORTS

import sys
sys.path.append('../api/sql wrapper')
import sql_wrapper as wrapper

from urllib.request import urlopen
import urllib
import requests
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from geopy.geocoders import Nominatim


def population_density(city='aurangabad'):
    '''
    GIves the population density of a city
    :param city: cite name
    :return: population density
    '''
    return 366

def calculate_drift(todays_intentensity, yesterdays_intensity, ppd):
    '''
    Calculates drift for a region
    :param todays_intentensity: intensity value for today
    :param yesterdays_intensity: intensity value for yesterday
    :param ppd: population density of that region
    :return: drift
    '''
    return (todays_intentensity - yesterdays_intensity) / ppd


def calculate_intensity(count, ppd, last_drift, last_intensity):
    '''
    calculates intensity for given parameters
    :param count: count of patient
    :param ppd: population density
    :param last_drift: drift of yesterday
    :param last_intensity: drift of today
    :return: intensity
    '''
    current_factor = count / ppd
    inflation_factor = last_drift * last_intensity

    return current_factor + inflation_factor


def threshold(intensity):
    '''
    Gives threshold for epidemic
    :param intensity: today's intensity
    :return: Boolean whether intensity is above threshold or not
    '''
    return intensity >= 0.01

def intensity_and_drift_of_dataframe(df, last_intensity, last_drift):
    '''
    Calculates intensity, drift and epidemic threshold of complete dataframe
    :param df: pandas dataframe
    :param last_intensity: intensity of yesterday
    :param last_drift: drift for yesterday
    :return: (intensity, drift, boolean for epidemic)
    '''

    count = len(df)
    ppd = population_density()

    intensity = calculate_intensity(count, ppd, last_drift, last_intensity)
    drift = calculate_drift(intensity, last_intensity, ppd)
    is_epidemic = threshold(intensity)

    return intensity, drift, is_epidemic

def get_surrounding_pincodes(pincode, sqlWrapper=None):
    '''
    Returns a list of surrounding pincodes of a given pincode
    :param pincode: pincode of the region
    :param sqlWrapper: Optional, if already made an sqlWrapper
    :return: list of surrounding pincodes
    '''
    if sqlWrapper is None:
        sqlWrapper = wrapper.SqlWrapper(password='')
    query = "select pincode from district_pincode where pincode like '" + str(pincode)[:4] + "%'"
    l = sqlWrapper.custom_query(query, single=True)
    return l


def internet_on():
    try:
        response = urlopen('https://www.google.com/', timeout=10)
        return True
    except:
        return False


def geopy_latlong_from_pincode(pincode):
    '''
    Get latlong of a pincode using geopy
    :param pincode: pincode of the area
    :return: (latitude, longitude)
    '''
    geolocator = Nominatim(user_agent="default")
    location = geolocator.geocode(str(pincode), timeout=40)
    if location is None:
        return pincode_to_coordinates(pincode)
    return (location.latitude, location.longitude)

def pincode_to_coordinates(pincode):
    '''
        Function to get coordinates from a zipcode using seleniuim and scraping google searches
        Parameters:
            1. pincode: pincode of the area whose coordinates is to be searched
        Returns:
            tuple of coordinates if found else None
    '''

    if pincode == "" or pincode is None:
        raise Exception('Pincode cannot be empty')

    #     req = requests.get('http://clients3.google.com/generate_204')
    if not internet_on():
        raise Exception('Error: Internet is not connected')

    text = str(pincode) + ' coordinates'
    text = urllib.parse.quote_plus(text)
    url = 'https://google.com/search?q=' + text

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(r'C:\chromedriver\chromedriver.exe', chrome_options=options)

    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")

    for g in soup.findAll('div', {'class': 'Z0LcW'}):
        if ' E' in str(g.text):
            driver.quit()
            lat, long = g.text.split(', ')
            lat = lat.replace('° N', '').strip()
            long = long.replace('° E', '').strip()
            return (lat, long)
    driver.quit()
    return None

def min_max_normalize(vals):
    '''
    Normalizes a pandas series according to min max normalization
    :param vals: pandas series
    :return: narmalized pandas series
    '''
    minimum = vals.min()
    maximum = vals.max()
    denominator = maximum - minimum
    if denominator <=0:
        denominator = 1
    return (vals - minimum) / denominator

# print(pincode_to_coordinates(431002))