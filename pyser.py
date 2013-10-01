#!/bin/python2

import re
import argparse
import subprocess
import os
from os import listdir
from os.path import isfile, join
import signal


filetypes=['mkv','avi','mpg','mp4']
mypath = "."
continue_file = join(mypath, ".series_continue")
keywords_pattern = re.compile(".*")
keywords = None

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

def read_int():
		line = raw_input()
		try:
			return int(line)
		except ValueError:
			print "Not a valid option, try again "
			return read_int() 

def read_bool(msg, yes='y', no='n', default=True):
	print msg + " ["+yes +"/" + no+"]"
	line = raw_input()
	if default and line.strip() != no:
		return True
	else:
		return line.strip() == yes

def menu(episode_no):
	applicable = [f for f in video_files() if check_episode(f, episode_no) ]
	if len(applicable) == 0:
		print "No matches found for episode " + str(episode_no)
		exit(0)
	list_files(applicable)
	chosen_option = read_int() - 1
	if len(applicable) > chosen_option:
		play_video( applicable[chosen_option] )
		write_continue(episode_no, applicable[chosen_option])
		menu(episode_no + 1)
	else:
		print "Invalid option chosen"
		menu(episode_no)

def tsuzuke():
	print "continuing..."
	last_ep = read_continue()
	if os.path.exists(continue_file):
		if read_bool("Done with "+ str(last_ep) + "?"):
			menu(last_ep + 1)
		else:
			menu(last_ep)
	else:
		menu(1)

def write_continue(episode_no, filename):
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
		print "Continue file exists - last episode watched = " + str(read_continue())
	else:
		print "No continue file"

def play(episode):
	menu(episode)
	
def play_video(filepath):
	MPLAYERLOG = open('mplayer.log', 'w')
	process = subprocess.Popen(["mplayer", join(mypath, filepath)], stdout=MPLAYERLOG, stderr=MPLAYERLOG)
	output = process.communicate()[0]
	print "Done playing video, next?"

all_numbers = re.compile('\d+') 
series_no = re.compile('.*[Ss]\d{2}[Ee](\d+)' )  #series syntax - blabla_S01E12
def check_episode(filename, episode):
	if not keywords_pattern.match(filename):
		return False

	if series_no.match(filename):
		return episode == int(series_no.match(filename).group(1))
	for number in all_numbers.finditer(filename):
		if episode == int(number.group(0)):
			return True
	return False



signal.signal(signal.SIGINT, signal.SIG_DFL)
parser = argparse.ArgumentParser(description='play stuff')

parser.add_argument('-c', '--continue', dest="tsuzuke", action='store_true',
                   help='Continue where left off previous time')

parser.add_argument('-s', '--status', dest="status", action='store_true', help='Does continue file exist')
parser.add_argument("episode", nargs="?", type=int, help='Number of episode')
parser.add_argument("-p", "--path", dest="path", help='Custom path, default is .')
parser.add_argument("-k", "--keywords", dest="keywords", help='Keywords for searching eps, comma separated')
args = parser.parse_args()

if(args.path != None):
	mypath = args.path
if(args.keywords != None):
	keywords = args.keywords.split(",")
	lookaround_keywords = [ ("(?=.*" + f + ")") for f in keywords ]
	str_regex = "^" + "".join(lookaround_keywords) + ".*$"
	keywords_pattern = re.compile(str_regex, re.IGNORECASE)
	

if args.status:
	status()

elif args.tsuzuke:
	tsuzuke()
else:
	if(args.episode == None):
		print "Please provide an episode number"
	else:
		play(args.episode)






