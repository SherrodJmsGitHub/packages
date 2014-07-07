#
#    Made by lowliet
#
import os
import sys

sys.path.append(os.path.join(os.path.abspath(".."), "gntp"))


from datetime import datetime


import sublime
import sublime_plugin


import gntp
import gntp.notifier as growl
from gntp.notifier import mini


STATUSBARTIME_FORMAT_KEY = 'StatusBarTime_format'
STATUSBARTIME_CLOCK_TYPE_KEY = 'StatusBarClock_Type'
STATUSBARTIME_SETTING_FILE = 'StatusBarTime.sublime-settings'
STATUSBARTIME_CLOCKDELAY_KEY = 'StatusBarClock_Interval'
STATUSBARTIME_CLOCKDISPLAY_ONLYINVIEW_KEY = "StatusBarClock_display_onlyinview"
STATUSBARTIME_LEFTY_KEY = 'StatusBarClock_lefty'
DEFAULT_FORMAT = '%H:%M:%S'

GrowlName="TimeGrowler";
GrowlNotification={"time":"time_growl"};
GrowlIcon=open("c:\\users\\cls\\pictures\\timercon.png", 'rb').read();

class StatusBarTime(sublime_plugin.EventListener):
    stBarStartTime = 0  # variable to hold start time
    def on_activated(self, view):
        settings = sublime.load_settings(STATUSBARTIME_SETTING_FILE)

        # Get Update interval for clock
        update_interval = settings.get(STATUSBARTIME_CLOCKDELAY_KEY, 1000)

        # New Setting load From setting file
        clock_Type = settings.get(STATUSBARTIME_CLOCK_TYPE_KEY, 0)

        # Get setting for only in view display
        onlyinview = settings.get(STATUSBARTIME_CLOCKDISPLAY_ONLYINVIEW_KEY, True)
        # Get setting for lefty display
        lefty = settings.get(STATUSBARTIME_LEFTY_KEY, True)

        # Start Timer if its empty (This is supposed to happen only once)
        if not self.stBarStartTime:
            self.stBarStartTime=datetime.now()

            register_notifier=growl.GrowlNotifier(
                applicationName=GrowlName,
                notifications=GrowlNotification.values(),
                applicationIcon=GrowlIcon)

            register_notifier.register();

            register_notifier.notify(
                description="Timer is running:%s" % datetime.now().strftime(DEFAULT_FORMAT),
                title="Time Growl",
                icon=GrowlIcon,
                noteType=GrowlNotification["time"]
                )

        if not clock_Type:
            timer=Timer(settings.get(STATUSBARTIME_FORMAT_KEY, DEFAULT_FORMAT))
            timer.displayTime(view, update_interval, onlyinview, lefty)
           

        else:
            Timer().displayUpTime(view, self.stBarStartTime, update_interval, onlyinview, lefty)

class Timer():
    growl_toggl=False
    
    break_time_count=1;

    wait_time=1;

    prev_time=datetime.now();

    status_key = 'statusclock'

    def __init__(self, format=DEFAULT_FORMAT):
        self._format = format

    # helper method which converts given duration to days, hours, minutes and seconds
    def convert_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = seconds//3600
        minutes = (seconds % 3600)//60
        seconds = seconds % 60
        return days, hours, minutes, seconds

    def displayTime(self, view, delay, onlyinview, lefty):
        if lefty:
            self.status_key = "__statusclock"        

       # view.set_status(self.status_key, now.strftime(self._format))

        actwin = sublime.active_window()
        if actwin:
            if not onlyinview or (actwin.active_view() and actwin.active_view().id() == view.id()):
                
                now=datetime.now();    
                minutes = self.convert_timedelta(now-Timer.prev_time)[2];                    

                if now.minute%15==0 and minutes>=Timer.wait_time:
                    Timer.break_time_count-=1;              
                    self.notify();
                    Timer.prev_time=now; 
                    Timer.wait_time=14;
                    
                sublime.set_timeout(lambda: self.displayTime(view, delay, onlyinview, lefty), delay)
        else:
            view.set_status(self.status_key, '')
        return

    # Method for handling uptime display
    def displayUpTime(self, view, startTime, delay, onlyinview):
        upTime = datetime.now() - startTime
        days, hours, minutes, seconds = self.convert_timedelta(upTime)
        out = ''
        if days: out += str("%s days, " % (days))
        if hours: out += str("%02d:%02d:%02d" % (hours, minutes, seconds))
        elif minutes: out += str("%02d:%02d" % (minutes, seconds))
        elif seconds: out += str("%02d seconds" % (seconds))
        view.set_status(self.status_key, out)
        actwin = sublime.active_window()
        if actwin:
            if not onlyinview or (actwin.active_view() and actwin.active_view().id() == view.id()):
               sublime.set_timeout(lambda: self.displayUpTime(view, startTime, delay, onlyinview), delay)
        else:
            view.set_status(self.status_key, '')
        return


    def notify(self):

        if 0<Timer.break_time_count:
            mini(
                applicationName=GrowlName,
                notificationIcon=GrowlIcon,
                description=datetime.now().strftime(self._format),
                title="TimeGrowl",
                noteType=GrowlNotification["time"])
        else:
            mini(
                applicationName=GrowlName,
                notificationIcon=GrowlIcon,
                description=datetime.now().strftime(self._format),
                title="TimeGrowl:Maybe take a break",
                noteType=GrowlNotification["time"])

            Timer.break_time_count=5;

