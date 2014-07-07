#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: CLS
# @Date:   05-07-2014 14:42:40
# @Last Modified by:   CLS
# @Last Modified time: 06-07-2014 06:26:10

#inspired by TogglAPI by Mosab Ahmad <mosab.ahmad@gmail.com>

import sys

import os
import json
import urllib2
from urllib import urlencode

import sublime, sublime_plugin

class API(object):
    """A wrapper for Toggl Api"""

    def __init__(self, api_url, api_token):
        self.api_token = api_token
        self.api_url=api_url
        self.show_trace=True;

    def make_url(self, section=None, params={}):
        """Constructs and returns an api url to call with the section of the API to be called
        and parameters defined by key/pair values in the paramas dict.
        Default section is "time_entries" which evaluates to "time_entries.json"

        >>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
        >>> t._make_url(section='time_entries', params = {})
        'https://www.toggl.com/api/v8/time_entries'

        >>> t = TogglAPI('_SECRET_TOGGLE_API_TOKEN_')
        >>> t._make_url(section='time_entries', params = {'start_date' : '2010-02-05T15:42:46+02:00', 'end_date' : '2010-02-12T15:42:46+02:00'})
        'https://www.toggl.com/api/v8/time_entries?start_date=2010-02-05T15%3A42%3A46%2B02%3A00%2B02%3A00&end_date=2010-02-12T15%3A42%3A46%2B02%3A00%2B02%3A00'
        """


        if section:
            url = self.api_url + "/"+ section+"?"

            if len(params) > 0:
                
                url = url + urlencode(params)

        else:
        	raise ValueError('No post section entered{}'.format(self.api_url));
        
        self.print_trace(url);

        return url


    def print_trace(self, arg):
        if self.show_trace:
            print("\n%s\n" %(arg,));

    def query(self, url):
        #Makes the actual query to the api
        self.print_trace(("url:%s\n", url))
    	try:
    		response=urllib2.urlopen(url);
    	except urllib2.HTTPError,e:
    		response="none";

        if response!="none":
            value=response.read() 
            #try for json
            try:
                response=json.loads(value)
            except ValueError, e:
                response=value;
            
            self.print_trace("response:%s\n" % response);

    	return response;


    def post(self, section, args):
        url=self.make_url(section, args);

        return self.query(url);