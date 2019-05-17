from bs4 import BeautifulSoup
import requests
import pymongo
from splinter import Browser
import pandas as pd
import time


def init_browser():
	executable_path = {"executable_path": 'chromedriver.exe'}
	return Browser("chrome", **executable_path, headless=False)


def scrape_info():
	browser = init_browser()

	# NASA Mars News
	news_url = "https://mars.nasa.gov/news/"
	browser.visit(news_url)
	
	time.sleep(1)

	html = browser.html
	news_soup = BeautifulSoup(html, 'html.parser')
	element_holder = news_soup.select_one('ul.item_list')

	title_list = []
	lede_list = []
	for result in element_holder:
		title = result.find('div', class_='content_title').text
		lede = result.find('div', class_='article_teaser_body').text
		title_list.append(title)
		lede_list.append(lede)


	# jpl featured image url
	jpl_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
	browser.visit(jpl_url)
	html = browser.html
	full_image = browser.click_link_by_id('full_image')

	time.sleep(1)

	image_moreifo = browser.find_link_by_partial_text('more info')
	image_moreifo.click()

	time.sleep(1)

	image = browser.find_by_tag('figure')
	image.click()

	time.sleep(1)

	html = browser.html
	jpl_soup = BeautifulSoup(html, 'html.parser')

	featured_image_url = jpl_soup.find('img')['src']


	# twitter
	twitter_url = 'https://twitter.com/marswxreport?lang=en'
	browser.visit(twitter_url)

	time.sleep(1)	

	html = browser.html
	twitter_soup = BeautifulSoup(html, 'html.parser')

	latest_tweet = twitter_soup.select_one('div.content p').text.strip('pic.twitter.com/R6BliV8xpj').replace('\n', ', ')

	# Mars facts
	facts_url = 'https://space-facts.com/mars/'
	browser.visit(facts_url)
	
	time.sleep(1)

	html = browser.html
	mars_facts = pd.read_html(html)
	mars_facts = mars_facts[0]
	mars_facts = mars_facts.to_html(columns=None, col_space=None, header=False, index=False)

	# Mars Hemispheres
	hem_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
	browser.visit(hem_url)
	
	time.sleep(1)

	html = browser.html
	hem_soup = BeautifulSoup(html, 'html.parser')
	hem_titles = hem_soup.find_all('h3')
	hem_titles = [title.text for title in hem_titles]

	hem_image_urls = []
	for title in hem_titles:
		hem_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
		browser.visit(hem_url)
		browser.click_link_by_partial_text(title)
		html = browser.html
		hem_soup = BeautifulSoup(html, 'html.parser')
		hem_image_url = hem_soup.find('a', target='_blank')['href']
		hem_image_urls.append(hem_image_url)

	hemisphere_image_urls = [
		{"title": hem_titles[0], "img_url": hem_image_urls[0]},
		{"title": hem_titles[1], "img_url": hem_image_urls[1]},
		{"title": hem_titles[2], "img_url": hem_image_urls[2]},
		{"title": hem_titles[3], "img_url": hem_image_urls[3]},
	]

	mars_data = {
		"NASA_Mars_News_Titles": title_list, 
		"NASA_Mars_News_Ledes": lede_list,
		"JPL_Featured_Image_URLs": featured_image_url,
		"Mars_Weather_Tweet": latest_tweet,
		"Mars_Space_Facts": mars_facts,
		"Mars_Hemispheres": hemisphere_image_urls,
	}

	browser.quit()
	
	return mars_data