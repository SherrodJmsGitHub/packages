
import os
import sys
import json
import ntpath
import sublime
import sublime_plugin


class ProjectDisplay(sublime_plugin.EventListener):
	def set_project(self):
		active_view=sublime.active_window().active_view()
		
		if active_view:
			#display the project name
			project=os.path.splitext( get_active_project() )[0]
			filename=ntpath.basename(active_view.file_name())

			if project==None: project="none"

			active_view.set_status("__projectlabel", project)
			active_view.set_status("filename", filename);

	def on_activated(self, view):
		self.set_project();

	def on_pre_save(self, view):
		self.set_project();
			

			
def get_active_project():
	#get auto save session_file
	settings_dir = os.path.join(sublime.packages_path(), '..', 'Settings')
	session_file='Auto Save Session.sublime_session'

	session_file=os.path.join(settings_dir, session_file)

	ses=None

	if os.path.exists(session_file):
	    with open(session_file, 'r') as input:
	        ses=json.loads(input.read(), strict=False)
	#if session_file cant be found try the normal session_file file
	else:
		session_file=os.path.join(settings_dir,"Session.sublime_session")
		if os.path.exists(session_file):
			with open(session_file, 'r') as input:
				ses=json.loads(input.read(), strict=False)

	if not ses:
		sys.stderr.write("cannot open any session file \n")
		return "none"	
		
	actwin=sublime.active_window();
	window_id = actwin.id()

	for w in ses['windows']:
	    if w['window_id'] == window_id:
	        project = w['workspace_name']

	        if not project: return "none"
	        else: return ntpath.basename(project);

		sys.stderr.write("could not find window id in auto session_file file\n")
		return "no-id"
	else:
		return "none";