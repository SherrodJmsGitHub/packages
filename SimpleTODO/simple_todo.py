import sublime, sublime_plugin
import os
import json
import urllib2
import ntpath
from threading import Thread

from todoist import TodoistAPI

SETTING_FILE_NAME = "SimpleTODO.sublime-settings";

class SimpleTodoListener(sublime_plugin.EventListener):
    def __init__(self):
        
        sublime.set_timeout(TodoistAPI.check, 0);
        
        self.refresh(sublime.active_window().active_view())


    def on_load(self, view):
        self.refresh(view)
        

    def on_activated(self, view):
        self.refresh(view)


    def refresh(self, view):
        if view.window() and view.window().folders():
            directory = view.window().folders()[0]
            settings = sublime.load_settings(SETTING_FILE_NAME)
            todo = settings.get(directory)

            if todo:
                regions = []
                for item in todo:
                    if view.file_name() == os.path.join(directory, item["file_name"]):
                        point = view.text_point(int(item["line_number"]) - 1 ,0)
                        regions.append(sublime.Region(point, point))

                view.add_regions("SimpleTodo", regions, "mark", "dot", sublime.HIDDEN)
           
       # 


class SimpleTodoCommand(sublime_plugin.TextCommand):
    def run(self, edit, mode):
        self.window = self.view.window()
        self.directory = self.window.folders()[0]

        settings=sublime.load_settings(SETTING_FILE_NAME);


        self.todoist=TodoistAPI();

        if mode == "add":
            self.add()
        elif mode == "list":
            self.list()


    def get_active_project(self):
        #get auto save session
        settings_dir = os.path.join(sublime.packages_path(), '..', 'Settings')
        ses_file = 'Auto Save Session.sublime_session'
        ses_file = os.path.join(settings_dir, ses_file)
        
        if os.path.exists(ses_file):
            with open(ses_file, 'r') as input:
                ses=json.loads(input.read(), strict=False)
        else:
            sys.stderr.write("auto session file does not exist\n")

        window_id = self.window.id()
        for w in ses['windows']:
            if w['window_id'] == window_id:
                project = w['workspace_name']

                if not project: return ""
                else: return ntpath.basename(project);

        sys.stderr.write("could not find window id in auto session file\n")
        return ""


    def add(self):
        def on_done(text):
            todo = self.load_todo()
            file_name = self.view.file_name().replace(self.directory + '/', '', 1)
            todo.insert(0, {
                "text": text,
                "file_name": file_name,
                "line_number": self.view.rowcol(self.view.sel()[0].begin())[0] + 1
            })
           
            TodoistAPI.add_item_async(text, self.get_active_project());
           
            self.save_todo(todo)
            self.list()
            


        sel = self.view.sel()[0]
        if not sel.begin() == sel.end():
            default_text = self.view.substr(sel).strip()
        else:
            default_text = ''

        self.window.show_input_panel('New TODO', default_text, on_done, None, None)
        self.view.run_command('save');
       


    def list(self):
        settings = self.load_settings()
        todo = settings.get(self.directory)
        if todo == None:
            todo = []

        def on_done(index):
            if index == 0:
                self.add()
            elif index >= 1:
                self.actions(todo[index - 1])

        items = [["+ New", ""]] + [[i["text"], "%s:%s" % (i["file_name"], int(i["line_number"]))] for i in todo]
        sublime.set_timeout(lambda: self.window.show_quick_panel(items, on_done), 0)

    def actions(self, item):
        def on_done(index):
            if index == 0:
                self.list()
            elif index == 1:
                view = self.window.open_file(os.path.join(self.directory, item["file_name"]))
                point = view.text_point(int(item["line_number"]) - 1 ,0)
                regison = view.line(point)
                view.sel().clear()
                view.sel().add(regison)
                view.show_at_center(regison)
            elif index == 2:
                todo = self.load_todo()
                todo.remove(item)
                self.save_todo(todo)
                self.list()
            elif index == 3:
                self.window.show_input_panel('Add Note', "", None, None, None)

        info = "%s - %s:%s" % (item["text"], item["file_name"], int(item["line_number"]))
        items = [['< Back', ''], ['> Jump', info], ['- Delete', ''], ["# Add Note"]]
        sublime.set_timeout(lambda: self.window.show_quick_panel(items, on_done), 0)

    def load_todo(self):
        settings = self.load_settings()
        todo = settings.get(self.directory)
        if todo == None:
            todo = []
        return todo

    def save_todo(self, todo):
        self.load_settings().set(self.directory, todo)
        self.save_settings()

    def load_settings(self):
        return sublime.load_settings(SETTING_FILE_NAME)

    def save_settings(self):
        sublime.save_settings(SETTING_FILE_NAME)
