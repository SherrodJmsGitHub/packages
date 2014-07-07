
import os
import sys
import json
import ntpath
import sublime
import sublime_plugin

class ProjectDisplay(sublime_plugin.EventListener):

	def on_activated(self, view):
		active_view=sublime.active_window().active_view()
		
		if active_view:
			#display the project name
			project=os.path.splitext(self.get_active_project())[0]
			filename=ntpath.basename(active_view.file_name())

			if project==None: project="none"

			active_view.set_status("__projectlabel", project)
			active_view.set_status("filename", filename);
			

			



	def get_active_project(self):
		self.window=sublime.active_window();

		#get auto save session
		settings_dir = os.path.join(sublime.packages_path(), '..', 'Settings')
		ses_file = 'Auto Save Session.sublime_session'
		ses_file = os.path.join(settings_dir, ses_file)

		ses=None

		if os.path.exists(ses_file):
		    with open(ses_file, 'r') as input:
		        ses=json.loads(input.read(), strict=False)
		else:
		    sys.stderr.write("auto session file does not exist\n")

		window_id = self.window.id()
		if ses:
			for w in ses['windows']:
			    if w['window_id'] == window_id:
			        project = w['workspace_name']

			        if not project: return ""
			        else: return ntpath.basename(project);

				sys.stderr.write("could not find window id in auto session file\n")
				return ""
		else:
			return "none";