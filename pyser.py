#!/bin/python2

import re
import argparse
import subprocess
import os
from os import listdir
from os.path import isfile, join


filetypes=['mkv','avi','mpg','mp4']
mypath = "."
continue_file = join(mypath, ".series_continue")

def video_files():
	return [ f for f in listdir(mypath) if (isfile(join(mypath,f)) and is_video_file(f)) ]

def is_video_file(f):
	for t in filetypes:
		if f.endswith(t):
			return True
	return False

def list_files(files):

	for (n,f) in enumerate(files):
		print str(n + 1) + ". " + f;

def menu(episode_no):
	applicable = [f for f in video_files() if check_episode(f, episode_no) ]
	if len(applicable) == 0:
		print "No matches found for episode " + str(episode_no)
		exit(0)
	list_files(applicable)
	line=input()
	chosen_option = int(line) - 1
	if len(applicable) > chosen_option:
		play_video( applicable[chosen_option] )
		write_continue(episode_no)
		menu(episode_no + 1)
	else:
		print "Invalid option chosen"
		menu(episode_no)

def tsuzuke():
	print "continuing..."
	last_ep = read_continue()
	if os.path.exists(continue_file):
		print "Done with "+ str(last_ep) + "? y/n "
		zaber = raw_input()
		if zaber == "" or zaber == "y":
			menu(last_ep + 1)
		else:
			menu(last_ep)
	else:
		menu(1)

def write_continue(episode_no):
	with open(continue_file, 'w') as content_file:
    		content_file.write(str(episode_no))

def read_continue():
	if os.path.exists(continue_file):
		with open(continue_file, 'r') as content_file:
			return int(content_file.read())
	else:
		print "No continue file, starting at episode 1"
		return 1	

def status():
	if os.path.exists(continue_file):
		print "Continue file exists " + str(read_continue())
	else:
		print "No continue file"

def play(episode):
	menu(episode)
	
def play_video(filepath):
	process = subprocess.Popen(["mplayer", join(mypath, filepath)], stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print "Done playing video"

all_numbers = re.compile('\d+') 
series_no = re.compile('.*[Ss]\d{2}[Ee](\d+)' )  #series syntax - blabla_S01E12
def check_episode(filename, episode):
	if series_no.match(filename):
		return episode == int(series_no.match(filename).group(1))
	for number in all_numbers.finditer(filename):
		if episode == int(number.group(0)):
			return True
	return False



parser = argparse.ArgumentParser(description='play stuff')

parser.add_argument('-c', '--continue', dest="tsuzuke", action='store_true',
                   help='Continue where left off previous time')

parser.add_argument('-s', '--status', dest="status",  help='Does continue file exist')
parser.add_argument("episode", nargs="?", type=int, help='Number of episode')
parser.add_argument("-p", "--path", dest="path", help='Custom path, default is .')
args = parser.parse_args()

if(args.path != None):
	mypath = args.path


if args.status != None:
	print status()
elif args.tsuzuke:
	tsuzuke()
else:
	if(args.episode == None):
		print "Please provide an episode number"
	else:
		play(args.episode)






