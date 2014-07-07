import sys

import os
import json
import urllib2
from datetime import datetime

import sublime, sublime_plugin
import threading
from threading import Thread

sys.path.append(os.path.join(sublime.packages_path(), "gntp"));
sys.path.append(os.path.join(sublime.packages_path(), "apibase"));

import gntp
import gntp.notifier

from api import API

RELEASE=True;
GrowlIcon=open("C:\\Program Files (x86)\\Todoist\\todoist.ico", 'rb').read();

settings = sublime.load_settings('todoist.sublime-settings');

class TodoistFactory:

	@staticmethod
	def create_project():
		n_project={
		  "name":"",
		  "color":0,
		  "collapsed":0,
		  "item_order":0,
		  "cache_count":0,
		  "indent":0,
		  "id":0,
		  "last_updated":""
		}

		return n_project;	

	@staticmethod
	def create_item():

		newitem={
			"token":"",
			"content": "",
			"due_date": "null",
			"collapsed": 0,
			"priority": 0,
			"project_id":0
		}

		return newitem;


	@staticmethod
	def create_note():

		newnote={
			"token":"",
	    	"item_id":0,
	    	"content":""
	    }

		return newnote;

class TodoistAPI(API):

	API="https://api.todoist.com/API/";
	APIOK=False;
	APITOKEN="";

	LOGFILE="";

	GrowlName="SimpleTodoist";	

	GrowlNotifications=["ping", "new_item"];


	@staticmethod
	def check():
		notifier=gntp.notifier.GrowlNotifier(
			applicationName=TodoistAPI.GrowlName,
			applicationIcon=GrowlIcon,
			notifications=TodoistAPI.GrowlNotifications)
		
		notifier.register();

		# A bit of chicanery to check if the api is there.
		# By pinging without a token it should respond asking 
		# for the token if all is ok.

		# try:
		# 	response=urllib2.urlopen(TodoistAPI.API+"ping");
		# except urllib2.HTTPError as e:
		# 	code=e.code
		# 	mssg=e.read();

		resp=TodoistAPI().ping();	

		if resp=="ok":
			TodoistAPI.APIOK=True
			
			sublime.status_message("todoist ok")
			
			notifier.notify(        
			noteType="ping",
		    title="Check Todoist Api",
		    icon=GrowlIcon,
		    description = "Todoist Ok")
		    
		else:
			TodoistAPI.APIOK=False
			notifier.notify(        
			noteType="ping",
		    title="Check Todoist Api",
		    icon=GrowlIcon,
		    description = "Cannot Connect to Api resp:[%d:%s]" % (code, mssg))


	def __init__(self,  is_logging_enabled=False):

		#api not tested so no token loaded
		if not TodoistAPI.APIOK:
			TodoistAPI.APITOKEN=settings.get('token');

		super(TodoistAPI, self).__init__(
			api_url="https://api.todoist.com/API",
			api_token=TodoistAPI.APITOKEN);


		self.logging_enabled=is_logging_enabled;

		self.project="Inbox"
		
		if len(sublime.windows())>0:
			self.project=sublime.windows()[0].folders()[0];
			
		self.logfile=open(sublime.packages_path() + "\\SimpleTodo\\todoisthandler.messages", "w");

		#if true automatically adds a new project if one cannot be found
		#else it will add to the inbox
		self.auto_add_project=True;
		
		self.log("TodoistAPI handler added for:%s\ncurrent project:%s\n" %(self.api_token, self.project));
	

	def __del__(self):
		if self.logfile.closed==False:
			self.logfile.flush();
			self.logfile.close();
			

	def log(self, logmssg):
		if self.logging_enabled:
			self.logfile.write(logmssg);
			self.logfile.flush();
		
		self.print_trace(logmssg);


#####################################
### Growl Helpers####################
	def notify_new_item(self, item, project):
		notifier=gntp.notifier.GrowlNotifier(
			applicationName=TodoistAPI.GrowlName,
			notifications=TodoistAPI.GrowlNotifications)

		desc="Added %d to %s\ncontent:%s" %(item["id"], project["name"], item["content"]);

		notifier.notify(        
		noteType="new_item",
		title="Added New Item",
		icon=GrowlIcon,
		description = desc)	


#####################################
### Api Helpers######################
	# Takes a dictionary and builds a query argument list string for the api
	# It automatically appends the API token
	def build_arg_string(self, hash):
		arg_string="";

		for key, value in hash.iteritems():
			arg_string += "%s=%s&" %(key, value);

	
		return arg_string[0:len(arg_string)-1].replace(" ","%%%d" % 20);
	
	@staticmethod
	def add_item_worker(text="", project_name=None):
		TodoistAPI().add_item(text, project_name);

	@staticmethod
	def add_item_async(text, project_name):
		sublime.set_timeout(lambda: TodoistAPI().add_item(text, project_name),0);		

	def add_item(self, text, project_name=None):
		project_id=0;
		self.log("entered add_item\nitem:\n%s\n" % (project_name));
		#Check for existing project
		project=self.get_project(project_name)
	


		# Adds a new item to directly to the inbox
		# this link describes the item data structure
		# http://api.todoist.com/API#Item%27s%20JSON%20properties
		newitem=TodoistFactory.create_item();
		newitem["token"]=self.api_token;
		newitem["content"]=text;
		newitem["project_id"]=project["id"];

		# Because there is no date added field a note is created that
		# has the date added
		note=TodoistFactory.create_note();
		note["content"]="created "+datetime.now().strftime('%d-%b-%Y')
		note["token"]=self.api_token;


		# self.log("entered add\nitem:\n%s\n\n" % (newitem));

		item_resp=self.post("addItem", newitem)

		if item_resp:
			note["item_id"]=item_resp["id"]

			if  self.post("addNote", note):			
				self.notify_new_item(item_resp, project)

		sublime.status_message('posted new item to todoist'+text);
		self.logfile.close();

	def ping(self):			
			self.log('ping:'+self.api_url);
			
			return self.post("ping", {"token":self.api_token});


	def get_project(self, project_name):
		project_id=0;

		if self.auto_add_project==False or project_name==None:
			project_name="Inbox"

		self.log("entered get_project_id\nitem:\n%s\n" % (project_name));		

		projects=self.post("getProjects", {"token":self.api_token});
		
		project=None;

		for project in projects:
			if project["name"]==project_name: break

		if project:
			self.log("found project:%s\n" % project["name"])
		else:
			self.log("adding project:%s" % project_name)
			addurl=self.make_url("addProject", {"name":project_name, "token":self.api_token})
			project=self.query(addurl,"POST");
			

		return project;
			

