from bs4 import BeautifulSoup
from pyfiglet import figlet_format
from slugify import slugify

import certifi, urllib3, json, xmltodict, requests, os, sys, shutil

INPUT_EXT1 = '.mp4'
OUT_EXT1 = '.mpg'
MP4_ALL_RECAPS_FILE = 'all-game-recaps.mp4'
VIDEO_QUALITY = 22 # 22=10300 Kbps, 23=, 24=6000 Kbps

recap_date_folder = '/videos/'
quality = '720'

http = urllib3.PoolManager(
	cert_reqs='CERT_REQUIRED',
	ca_certs=certifi.where()
)

def get_collection_uuid():
	collection_uuid = ''
	url = 'http://www.nba.com/video/gamerecaps'
	response = http.request('GET', url)
	soup = BeautifulSoup(response.data, 'html.parser')
	for link in soup.find(type="application/json"):
		game_recap_json = json.loads(link)
		return game_recap_json['collection_uuid']

def save_recap_video(content_xml):
	url = 'http://www.nba.com' + content_xml;
	response = http.request('GET', url)
	data = xmltodict.parse(response.data)
	for video in data['video']['files']['file']:
		if 'x' + quality in video['@bitrate']:
			print('Downloading "' + data['video']['headline'] + '"')
			r = requests.head(video['#text'], allow_redirects=True)
			output_folder = os.path.dirname(os.path.realpath(__file__)) + recap_date_folder
			output_filename = output_folder + '/' + slugify(data['video']['headline']) + '.mp4'
			if not os.path.isdir(output_folder):
				os.makedirs(output_folder)
			response = http.request('GET', r.url, preload_content=False)
			f = open(output_filename, 'wb')
			f.write(response.data)
			f.close()

def get_content(collection_uuid, date):
	url = 'https://api.nba.net/0/league/collection/' + collection_uuid
	response = http.request('GET', url)
	results = json.loads(response.data)
	for recap in results['response']['result'][0]['content']:
		if date in recap['url']:
			save_recap_video(recap['contentXml'])

def merge_game_recaps():
	mpg_file_list = list()
	dir_path = os.path.dirname(os.path.realpath(__file__)) + recap_date_folder
	tmp_path = dir_path + '/tmp'
	if not os.path.isdir(tmp_path):
		os.makedirs(tmp_path)
	for infile in os.listdir(dir_path):
		print(infile.lower())
		if infile.lower().endswith(INPUT_EXT1):
			outfile = tmp_path + '/' + infile + OUT_EXT1
			cmd = 'ffmpeg -i ' + dir_path + '/' + infile + ' -qscale:v 1 ' + outfile
			os.system(cmd)
			mpg_file_list.append(outfile)
	mpg_files_str = ''
	for mpg_file in mpg_file_list:
	    mpg_files_str = mpg_files_str + mpg_file + '|'
	cmd = 'ffmpeg -i concat:"' + mpg_files_str + '" -c:v libx264 -preset slow -crf ' + str(VIDEO_QUALITY) + ' -c:a aac -strict -2 ' + dir_path + '/' + MP4_ALL_RECAPS_FILE
	os.system(cmd)
	shutil.rmtree(tmp_path)

print(figlet_format('NBA Game Recaps', font='banner3'));

date = input('Choose a date (YYYY/MM/DD): ')

recap_date_folder += date

collection_uuid = get_collection_uuid()
get_content(collection_uuid, date)

merge_game_recaps()