#!/bin/python2

import re
import argparse
import subprocess
import os
from os import listdir
from os.path import isfile, join, walk
import signal


filetypes=['mkv','avi','mpg','mpe', 'mpeg', 'mp4', 'flv', 'mov', 'wmv', 'asf']
mypath = "./"
keywords_pattern = re.compile(".*")
keywords = None
deep = True
MAX_DEPTH = 2

def video_files():
	if not deep:
		return [ f for f in listdir(mypath) if (isfile(join(mypath,f)) and is_video_file(f)) ]
	else :
		return deep_files(mypath, 1)

def deep_files(dir, depth):
	found_files = []
	if depth > MAX_DEPTH:
		return []

	for root, dirs, files in os.walk(mypath):
		found_files = found_files + [ join(root,f) for f in files if (isfile(join(root,f)) and is_video_file(f)) ]
	return found_files 


def is_video_file(f):
	for t in filetypes:
		if f.lower().endswith(t):
			return True
	return False

def list_files(files):
	for (n,f) in enumerate(files):
		print str(n + 1) + ". " + os.path.basename(f)

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

def latest():

	applicable = [ get_episode_no(f) for f in video_files() if check_keyword(f) and get_episode_no(f) != -1 ]
	if len(applicable) > 0:
		menu( sorted(applicable)[-1] )
	else:
		print "Nothing found - only proper series syntax is supported e.g S01E01 etc."


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

#REGEX STUFF
all_numbers = re.compile('\d+') 
series_no = re.compile('.*[Ss]?\d+[EeXx](\d+)')  #series syntax - blabla_S01E12, blabla-1x2 etc

def check_keyword(filename):
	return keywords_pattern.match(filename)

def check_episode(filename, episode):
	if not check_keyword(filename):
		return False

	if series_no.match(filename):
		return episode == get_episode_no(filename)
	for number in all_numbers.finditer(filename):
		if episode == int(number.group(0)):
			return True
	return False

def get_episode_no(filename):
	if series_no.match(filename):
		return int(series_no.match(filename).group(1))
	#Not series syntax - return the first number found
	return int(re.compile('.*?(\d+)').match(filename).group(1))

	




signal.signal(signal.SIGINT, signal.SIG_DFL)
parser = argparse.ArgumentParser(description='play stuff')

parser.add_argument('-c', '--continue', dest="tsuzuke", action='store_true',
                   help='Continue where left off previous time')

parser.add_argument('-s', '--status', dest="status", action='store_true', help='Does continue file exist')
parser.add_argument('-d', '--deep', dest="deep", action='store_true', help='Search deep for files - default true', default=True)
parser.add_argument("episode", nargs="?", type=int, help='Number of episode')
parser.add_argument("-p", "--path", dest="path", help='Custom path, default is .')
parser.add_argument("-k", "--keywords", dest="keywords", help='Keywords for searching eps, comma separated')
parser.add_argument("-l", "--latest", dest="latest", help="The last episode available")
args = parser.parse_args()

def init_keywords(keywords_raw):
	keywords = keywords_raw.split(",")
	lookaround_keywords = [ ("(?=.*" + f + ")") for f in keywords ]
	str_regex = "^" + "".join(lookaround_keywords) + ".*$"
	keywords_pattern = re.compile(str_regex, re.IGNORECASE)

if(args.path != None):
	mypath = join(mypath, args.path)
	print mypath

continue_file = join(mypath, ".series_continue")

if(args.keywords != None):
	init_keywords(args.keywords)

if args.status:
	status()

elif args.tsuzuke:
	tsuzuke()
elif args.latest:
	init_keywords(args.latest)
	latest()
else:
	if(args.episode == None):
		print "Please provide an episode number"
	else:
		play(args.episode)






