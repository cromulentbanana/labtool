from __future__ import print_function

import base64
import datetime
import os
import json
import re
import urllib
import urllib2
import subprocess
import sys
from ConfigParser import SafeConfigParser
import getpass
import types

from config import __version__

class CustomJSONEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, datetime.datetime):
			return str(o)
		return super(CustomJSONEncoder, self).default(o)

class RestHandler(object):
	# vars used for http-connection/by RestHandler
	labUser = None
	_apikey = None
	_apiurl = None
	_glocalConf = None
	_localConf = None
	_opener = None
	_userConfigPath = None
	_serialization_classes = []
	interactive = True

	# vars for rest object
	restFields = None
	restPhonyFields = []

	@staticmethod
	def initialize(globalConfigPath, interactive=True):
		RestHandler.interactive = interactive

		# read global config
		config = SafeConfigParser()
		config.read(globalConfigPath)

		RestHandler._apiurl = config.get("labcli", "apiurl").rstrip("/")
		RestHandler._install_rest_opener()
		RestHandler._userConfigPath = os.path.expanduser(config.get("labcli", "userconf"))

		userConfig = SafeConfigParser()
		userConfig.read(RestHandler._userConfigPath)
		
		RestHandler._globalConf = config
		RestHandler._userConf = userConfig

		# read local config if present
		if not userConfig.has_section("labcli"):
			userConfig.add_section("labcli")

		# if no user is present use current one
		if not userConfig.has_option("labcli", "user"):
			currentUser = subprocess.check_output("whoami", shell=True).strip()
			userConfig.set("labcli", "user", currentUser)
		RestHandler.labUser = userConfig.get("labcli", "user")

		if userConfig.has_option("labcli", "apikey"):
			RestHandler._apikey = userConfig.get("labcli", "apikey")
		elif interactive:
			# interactively negotiate apikey
			print("No apikey present for this user, fetching key...", file=sys.stderr)
			RestHandler._negotiateApiKey()

	@classmethod
	def from_dict(clazz, data):
		""" Helper to create a rest based object from a python dict/json dump.

		Throws a ValueError if not all necessary fields are supplied.
		Returns object with given object class (clazz) on success
		"""
		for field in clazz.restFields:
			if field not in data:
				raise ValueError("Dictionary is missing field '%s' for conversion to %s class" % (field, clazz.__name__))
		return clazz(**dict(filter(lambda (key, val): key in clazz.restFields, data.items())))

	def to_dict(self):
		return self.data

	def __getattr__(self, name):
		if hasattr(self, "data") and name in self.data:
			return self.data[name]

		raise AttributeError("type object '%s' has no attribute '%s' and is not part of the rest dictionary" % (type(self).__name__, name))

	def __setattr__(self, name, value):
		if hasattr(self, "data"):
			#and name in self.data:
			self.data[name] = value
		else:
			self.__dict__[name] = value

	def __hasattr__(self, name):
		if hasattr(self, name):
			return True
		return name in self.data

	@staticmethod
	def add_serialization_class(clazz):
		RestHandler._serialization_classes.append(clazz)

	@staticmethod
	def _install_rest_opener():
		o = urllib2.build_opener()
		o.add_headers = [
			# Supply our own User-Agent 
			('User-agent', 'labcli/%s' % __version__),
			# If we send anything, we send JSON
			('Content-Type', 'application/json')
		]
		if RestHandler.labUser and RestHandler._apikey:
			o.add_headers.append(
				('Authorization', 'ApiKey %s:%s' % (RestHandler.labUser, RestHandler._apikey))
			)

		RestHandler._opener = o

	@staticmethod
	def _gen_headers(add_auth=True):
		headers = [
			# Supply our own User-Agent 
			('User-agent', 'labcli/%s' % __version__),
			# If we send anything, we send JSON
			('Content-Type', 'application/json')
		]

		if add_auth and RestHandler.labUser and RestHandler._apikey:
			headers.append(
				('Authorization', 'ApiKey %s:%s' % (RestHandler.labUser, RestHandler._apikey))
			)

		return headers

	def getObject(self, key):
		return self._getResource(key)

	@staticmethod
	def _getJsonResourceSimple(*args, **kwargs):
		""" Extra version of _getJsonResource which eats ValueErrors """
		try:
			return RestHandler._getJsonResource(*args, **kwargs)
		except ValueError:
			return None

	@staticmethod
	def _getJsonResource(*args, **kwargs):
		return json.loads(RestHandler._getResource(*args, **kwargs), object_hook=RestHandler._jsonObjectHook)

	@staticmethod
	def _mgetJsonResource(*args, **kwargs):
		return json.loads(RestHandler._mgetResource(*args, **kwargs), object_hook=RestHandler._jsonObjectHook)

	@staticmethod
	def _jsonObjectHook(d):
		if isinstance(d, types.DictType):
			for clazz in RestHandler._serialization_classes:
				try:
					return clazz.from_dict(d)
				except ValueError:
					pass
		return d

	@staticmethod
	def _mgetResource(links):
		# merge apilinks
		linkre = re.compile("^(/.*/)(\d+)/$")
		baselink = None
		nums = set()
		for link in links:
			m = linkre.match(link)
			if not m:
				raise ValueError("'%s' is not a valid (or supported) api link" % link)

			if baselink:
				if baselink != m.group(1):
					raise ValueError("link '%s' is not of the same object type (previous type was '%s'" % (link, baselink))
			else:
				baselink = m.group(1)

			nums.add(m.group(2))

		if not baselink:
			raise ValueError("No links given (linkset was %s)" % links)


		reqlink = "%sset/%s/?limit=0" % (baselink, ";".join(nums))

		return RestHandler._getResource(reqlink)

	@staticmethod
	def _getResource(resurl, method='GET', data=None, user_pass=None, interactive=None, _is_retry=False):
		if interactive is None:
			interactive = RestHandler.interactive
		resurl = resurl.lstrip("/")
		#print("Getting %s/%s" % (RestHandler._apiurl, resurl))
		url = "%s/%s" % (RestHandler._apiurl, resurl)
		r = urllib2.Request(url)
		r.get_method = lambda method=method: method

		for header in RestHandler._gen_headers(add_auth=(user_pass is None)):
			r.add_header(*header)

		if user_pass:
			authinfo = base64.b64encode("%s:%s" % user_pass)
			r.add_header('Authorization', 'Basic %s' % authinfo)

		if data is not None:
			r.add_data(json.dumps(data, cls=CustomJSONEncoder))

		try:
			res = urllib2.urlopen(r)
			return res.read()
		except urllib2.HTTPError as e:
			if e.code == 401:
				if interactive and not user_pass and not _is_retry:
					RestHandler._negotiateApiKey()
					return RestHandler._getResource(resurl, method, data, _is_retry=True)
				else:
					raise e
			elif e.code == 400:
				# Bad Request normally indicates that our query was somewhat unsucessfull
				# ==> we are going to return the api's error message
				return e.read()
			else:
				print("-"*30, "Error", "-"*30, file=sys.stderr)
				if 'Authorization' in r.headers:
					newAuth = re.sub("^([^ ]+) ([^:]+):(.*)", r"\1 \2:<redacted>", r.headers['Authorization'])
					r.headers['Authorization'] = newAuth
				import base64, zlib
				print("-----BEGIN BASE64/GZIP BLOB-----", file=sys.stderr)
				print(base64.encodestring(zlib.compress(e.read())), file=sys.stderr)
				print("-----END BASE64/GZIP BLOB-----", file=sys.stderr)
				import traceback
				traceback.print_stack(file=sys.stderr)
				print("", file=sys.stderr)
				print("Url:", r.get_full_url(), file=sys.stderr)
				print("Method:", r.get_method(), file=sys.stderr)
				print("Headers:", r.headers, file=sys.stderr)
				print("Data:", r.data, file=sys.stderr)
				print("", file=sys.stderr)
				print("Rest-API error - debug information above; everything necessary to send in a bug report", file=sys.stderr)

				sys.exit(1)

	@staticmethod
	def _negotiateApiKey():
		# get user/pass
		key = None
		keys = None
		user_pass = None
		for pwtry in range(3):
			password = getpass.getpass("Password for user %s: " % RestHandler.labUser)
			try:
				user_pass = (RestHandler.labUser, password)
				keys = RestHandler._getResource("/api/apikey/", user_pass=user_pass, interactive=False)
				break
			except urllib2.HTTPError as e:
				if e.code != 401:
					raise e

		if keys is None:
			# no password for key ==> quit
			print("Could not authenticate to labcli api", file=sys.stderr)
			sys.exit(1)

		# search current apikey
		keys = json.loads(keys)
		if len(keys["objects"]) > 0:
			key = keys["objects"][0]["key"]
		else:
			# if none is present, create one
			newKey = RestHandler._getResource("/api/apikey/", method="POST", data={}, interactive=False, user_pass=user_pass)
			key = json.loads(newKey)["key"]

		RestHandler._apikey = key

		# test if apikey works
		try:
			keys = RestHandler._getResource("/api/apikey/", interactive=False)
			
		except urllib2.HTTPError as e:
			if e.code != 401:
				raise e
			print("Could not gather apikey for user, manual intervention needed.", file=sys.stderr)
			sys.exit(2)
		# save apikey in class/userfile
		RestHandler._userConf.set("labcli", "apikey", key)
		RestHandler._writeUserConf()

	@staticmethod
	def _writeUserConf():
		try:
			f = open(RestHandler._userConfigPath, "w")
			RestHandler._userConf.write(f)
			f.close()
		except IOError as e:
			print("Could not save user config to %s: %s" % (RestHandler._userConfigPath, str(e)), file=sys.stderr)


	@staticmethod
	def toUriDict(mylist):
		ret = {}
		for obj in mylist:
			if hasattr(obj, "resource_uri"):
				ret[obj.resource_uri] = obj
			else:
				ret[obj["resource_uri"]] = obj
		return ret

	@staticmethod
	def resolveLinks(objList, param):
		if len(objList) == 0:
			return objList
		getList = [getattr(obj, param) for obj in objList if getattr(obj, param) is not None]
		if len(getList) == 0:
			return objList

		flattend = None
		isList = False
		if type(getList[0]) == list:
			flattend = reduce(lambda x, y: x+y, getList, [])
			isList = True
		else:
			flattend = getList

		retList = RestHandler._mgetJsonResource(flattend)["objects"]
		retDict = RestHandler.toUriDict(retList)
		for obj in objList:
			if not getattr(obj, param):
				continue

			if isList:
				setattr(obj, param, [
					retDict[link] for link in getattr(obj, param)
				])
			else:
				setattr(obj, param, retDict[getattr(obj, param)])

		return objList

	def save(self):
		method = None
		apiurl = self.api_url
		if self.resource_uri is not None:
			# update
			method = 'PUT'
			apiurl = self.resource_uri
		else:
			method = 'POST'
		return self._getJsonResourceSimple(apiurl, method, data=self.data)

	def delete(self):
		return self._getJsonResourceSimple(self.resource_uri, method="DELETE")

	@classmethod
	def from_uri(clazz, uri):
		return clazz._getJsonResource(uri)

	@classmethod
	def find(clazz, **args):
		args['limit'] = 0
		url = "%s?%s" % (clazz.api_url, urllib.urlencode(args))
		return clazz._getJsonResource(url)["objects"]

	@classmethod
	def get_objects(clazz, resolve_links=True, **args):
		if not args:
			args = {}
		if "limit" not in args:
			args['limit'] = 0
		uri = "%s?%s" % (clazz.api_url, urllib.urlencode(args))
		objsMeta = clazz._getJsonResource(uri)
		objs = objsMeta["objects"]

		if resolve_links and hasattr(clazz, "linkFields"):
			for field in clazz.linkFields:
				objs = clazz.resolveLinks(objs, field)

		return objs

	@classmethod
	def get_apilink_list(clazz, *args, **kwargs):
		return clazz._mgetJsonResource(*args, **kwargs)["objects"]
