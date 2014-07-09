# Copyright (C) 2013 Christopher "Kasoki" Kaster
#
# This file is part of "FancyProjects". <http://github.com/Kasoki/FancyProjects>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import os

class ProjectStructure:
	def __init__(self, path, json):
		self.path = path
		self.name = json["name"]
		self.description = json["description"]
		self.default_project_name = json["default_project_name"]
		self.settings = json["settings"]
		self.build_systems = json["build_systems"]
		self.has_project_proto=False
		self.proto_file=""


	def to_quickpanel_item(self):
		return [self.name, self.description]


	def __str__(self):
		return self.name


	def check_for_protoproj(self):
			items=os.listdir( self.path );

			for item in items:
				if item.endswith(".project-proto"):
					self.has_project_proto=True;
					self.proto_file=os.path.join(self.path,item);
					break;