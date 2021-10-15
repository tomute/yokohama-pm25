#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# This python program regularly gets PM2.5 data from Yokohama city site and tweet the data.
#
import sys
import urllib2
import tweepy
import secret
from bs4 import BeautifulSoup
from google.appengine.ext import db

# Class for posting texst to Twitter.
class TwitterAuth(object):
	def getAuth(self):
		auth = tweepy.OAuthHandler(secret.CONSUMER_KEY, secret.CONSUMER_SECRET)
		auth.set_access_token(secret.TOKEN_KEY, secret.TOKEN_SECRET)
		oauthapi = tweepy.API(auth)
		return oauthapi

	def update(self, oauthapi, post):
		if post != '':
			oauthapi.update_status(post.encode('utf-8'))

# Class for DB access.
class Pm25Data(db.Model):
	time = db.StringProperty(required=True)

# Debug
# print 'Content-Type: text/plain'
# print ''

#
# Start main steps.
#
places = [u'鶴見', u'神奈川', u'港北', u'磯子', u'保土ヶ谷', u'西', u'金沢', u'中', u'港南', u'旭', u'瀬谷', u'南', u'栄', u'緑', u'青葉', u'都筑', u'泉', u'浅間下', u'戸塚', u'青葉台']

url = 'https://cgi.city.yokohama.lg.jp/kankyou/saigai/data/pm25_top_data.html'
html = urllib2.urlopen(url).read()
soup = BeautifulSoup(html, from_encoding='Shift_JIS')

# Get update time with the exception of parentheses.
time = soup.find('h2', class_='pm25').string[6:-1]
data = time + u' (μg/m³) '
hour = int(time[time.rfind(u'日') + 1:time.rfind(u'時')])

q = Pm25Data.all()
if q.count != 0:
	results = q.fetch(1)
	for p in results:
		if p.time == time:
			# No new data
			data = ''
		else:
			# Delete old data.
			db.delete(p)

# Cut 1st row to ignore the table header.
trs = soup.findAll('tr')[1:]
if len(trs) == len(places) and data != '':
	# If table format isn't modified.
	for i in range(0, len(places)):
		tds = trs[i].findAll('td')
		data = data + places[i] + tds[hour - 1].get_text().strip() + u' '
	data = data + u'#yokohama'
	# Store time.
	pm25data = Pm25Data(time=time)
	pm25data.put()

# Debug
# print data.encode('utf-8')

# Post the data to Twitter.
twitter = TwitterAuth()
twitterapi = twitter.getAuth()
twitter.update(twitterapi, data);
