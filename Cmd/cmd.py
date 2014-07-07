#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: CLS
# @Date:   13-06-2014 22:07:54
# @Last Modified by:   CLS
# @Last Modified time: 13-06-2014 22:08:11

import os, sublime_plugin
class CmdCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        file_name=self.view.file_name()
        path=file_name.split("\\")
        current_driver=path[0]
        path.pop()
        current_directory="\\".join(path)
        command= "cd "+current_directory+" & "+current_driver+" & start cmd"
        os.system(command)
