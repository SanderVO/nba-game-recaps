from bs4 import BeautifulSoup

import urllib, urllib2, json, xmltodict, requests

def get_collection_uuid():
	collection_uuid = ''
	url = 'http://www.nba.com/video/gamerecaps'
	data = urllib2.urlopen(url)
	soup = BeautifulSoup(data)
	for link in soup.find(type="application/json"):
		collection_uuid = json.loads(link)['collection_uuid']
	return collection_uuid

def get_num_of_games(date):
	url = 'https://data.nba.net/prod/v2/calendar.json'
	response = urllib2.urlopen(url)
	results = json.loads(response.read())
	return results[date]

def get_content_xml(collection_uuid):
	url = 'https://api.nba.net/0/league/collection/' + collection_uuid
	response = urllib2.urlopen(url)
	results = json.loads(response.read())
	return results['response']['result'][0]['content'][0]['contentXml']

def get_recap_video(content_xml):
	url = 'http://www.nba.com' + content_xml;
	file = urllib2.urlopen(url)
	data = file.read()
	file.close()
	data = xmltodict.parse(data)
	for video in data['video']['files']['file']:
		if 'x1080' in video['@bitrate']:
			return video['#text']

num_games = get_num_of_games('20190224')
collection_uuid = get_collection_uuid()
content_xml = get_content_xml(collection_uuid)
video_url = get_recap_video(content_xml)

r = requests.head(video_url, allow_redirects=True);

print r.url;

testfile = urllib.URLopener()
testfile.retrieve(r.url, 'recap.mp4')