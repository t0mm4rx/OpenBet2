import os
import json
import path
import requests
import numpy as np
import path

def get_programme(date, use_cache=True):
	URL = "https://tablette.turfinfo.api.pmu.fr/rest/client/1/programme/{}".format(date)
	FILE = "{}cache/programmes/{}.json".format(path.PATH, date)
	if (use_cache):
		if (os.path.exists(FILE)):
			return json.loads(open(FILE, "r").read())
	print("Downloading programme {}".format(date))
	try:
		result = requests.get(URL)
	except:
		print("Cannot download {}, retrying...".format(date))
		return get_programme(date)
	try:
		result_json = json.loads(result.text.replace('\r\n', ''))
		if (not "programme" in result_json):
			print("Cannot download programme {}".format(date))
			return -1
		with open(FILE, "w+") as file:
			file.write(json.dumps(result_json["programme"]))
		return result_json["programme"]
	except:
		print("Cannot download programme {}".format(date))
		return -1

def get_participants(date, reunion, course, use_cache=True):
	URL = "https://tablette.turfinfo.api.pmu.fr/rest/client/1/programme/{}/R{}/C{}/participants".format(date, reunion, course)
	FILE = "{}cache/participants/{}.json".format(path.PATH, "{}-{}-{}".format(date, reunion, course))
	if (use_cache):
		if (os.path.exists(FILE)):
			return json.loads(open(FILE, "r").read())
	print("Downloading race {} R{} C{}".format(date, reunion, course))
	try:
		result = requests.get(URL)
	except:
		print("Cannot download {} R{}C{}, retyring...".format(date, reunion, course))
		return get_participants(date, reunion, course)
	try:
		result_json = json.loads(result.text)
		if (not "participants" in result_json):
			print("Cannot download {} R{}C{}".format(date, reunion, course))
			return -1
		with open(FILE, "w+") as file:
			file.write(json.dumps(result_json))
		return result_json
	except:
		print("Cannot download {} R{}C{}".format(date, reunion, course))
		return -1

def get_course(date, reunion, course, use_cache=True):
	FILE = "{}cache/courses/{}.json".format(path.PATH, "{}-{}-{}".format(date, reunion, course))
	if (use_cache):
		if (os.path.exists(FILE)):
			return json.loads(open(FILE, "r").read())
	programme = get_programme(date, use_cache)
	if (programme == -1):
		return -1
	participants = get_participants(date, reunion, course, use_cache)
	if (participants == -1):
		return -1
	try:
		participants = participants["participants"]
		course_obj = programme["reunions"][reunion - 1]["courses"][course - 1]
		finish = course_obj["arriveeDefinitive"]
		result = {
			'finish': finish,
			'horses': participants
		}
		if (finish):
			finishOrder = list(np.array(course_obj["ordreArrivee"], dtype=np.int32).flatten())
			result['result'] = course_obj["ordreArrivee"]
		with open(FILE, "w+") as file:
			file.write(json.dumps(result))
		return result
	except:
		return -1

def go_through_courses(fn):
	for filename in os.listdir("{}cache/participants/".format(path.PATH)):
		filename = filename.split(".")[0]
		splits = filename.split("-")
		date = splits[0]
		reunion = int(splits[1])
		course = int(splits[2])
		obj = get_course(date, reunion, course)
		if (obj != -1):
			fn(obj)
