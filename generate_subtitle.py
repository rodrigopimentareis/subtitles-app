import json
import requests
import urllib
import subprocess
import os
import argparse	

def convert_to_flac(media_path):

	filename, file_extension = os.path.splitext(media_path)
	flac_file = media_path.replace(file_extension,'.flac')

	if os.path.isfile(flac_file):
		os.remove(flac_file)

	cmd = "./ffmpeg -i " + media_path + " -c:a flac -ar 16000  " + flac_file
	subprocess.call(cmd, shell=True)  
	return flac_file

def speech_recognition(flac_file_name, keywords, language):
	USERNAME="c7db9acd-189e-45d6-a9f1-a8724d2d4ccd"
	PASSWORD="jeKcaOBtl1XP"

	keywords_option = urllib.urlencode({"keywords" : keywords, "keywords_threshold":0.5})
	watson_url = "https://stream.watsonplatform.net/speech-to-text/api/v1/recognize?continuous=true&timestamps=true&model="+language + "&" + keywords_option
	headers = {'Content-Type': 'audio/flac'}
	data = file(flac_file_name, "rb").read()


	r = requests.post(watson_url, data=data,auth=(USERNAME,PASSWORD),headers=headers)

	return r.content
	
def convert_to_str_time(time_float):
	#convert time in ss::milisecond to hh:mm:ss:milisecond
	m, s = divmod(time_float, 60)
	h, m = divmod(m, 60)
	milisec = int(str(time_float).split('.')[-1])
	ts = "%02d:%02d:%02d,%03d" % (h, m, s, milisec)
	return ts

def read_subtitles_file(file_name):
	#read results of speech recognition
	subtitles_file = open(file_name)
	content_str = subtitles_file.read().decode('utf8')
	subtitles_file.close()
	return content_str


def generate_srt(subtitles_file_name, content_str):
	#generate a .str file
	
	#open json
	content_object = json.loads(content_str)

	#create new file
	results_file_name = subtitles_file_name.replace(".flac",".srt")
	results_file = open(results_file_name,'w')

	#navigate results
	results = content_object['results']
	number = 1
	for r in results:
		#always use first alternative
		alternative = r['alternatives'][0]

		timestamps = alternative['timestamps']
		
		#Get beggining and ending of the phrase
		initial_time = convert_to_str_time(timestamps[0][1])
		final_time = convert_to_str_time(timestamps[-1][-1])
		#Get the transcript in unicode formate
		transcript = alternative['transcript'].encode('utf8')

		#Write results in .srt format
		results_file.write(str(number)+"\n")
		results_file.write(initial_time + " --> " + final_time+"\n")
		results_file.write(transcript+"\n\n")
		number += 1
	results_file.close()

def generate_txt(subtitles_file_name, content_str):
	#generate a .str file
	
	#open json
	content_object = json.loads(content_str)

	#create new file
	results_file_name = subtitles_file_name.replace(".flac",".txt")
	results_file = open(results_file_name,'w')

	#navigate results
	results = content_object['results']
	for r in results:
		#always use first alternative
		alternative = r['alternatives'][0]

		#Get the transcript in unicode formate
		transcript = alternative['transcript'].encode('utf8')

		#Write results in .srt format
		print transcript
		results_file.write(transcript+"\n")
	results_file.close()


def main():

	parser = argparse.ArgumentParser(description='Generate subtitles for a audio or movie file.')
	parser.add_argument('file_name', help='Name of the file of the movie or audio to be processed.')
	args = parser.parse_args()

	file_name = args.file_name
	if not os.path.isfile(file_name):
		quit(file_name + " was not found!")


	keywords = ["Jenkins","git","Plug-ins"]
	#language = "pt-BR_BroadbandModel"
	language = "en-US_BroadbandModel"
	
	file_name = convert_to_flac(file_name)
	speech_result = speech_recognition(file_name, keywords, language)
	generate_srt(file_name, speech_result)
	generate_txt(file_name, speech_result)

#execute main
main()	

