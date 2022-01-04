from pathlib import Path
from tkinter import *
import os, re

class SuspiciousOperation(Exception):
    """The user did something suspicious"""

class SuspiciousFileOperation(SuspiciousOperation):
    """A Suspicious filesystem operation was attempted"""
    pass

def get_folder_size(folder):
	return convert_bytes(sum(file.stat().st_size for file in Path(folder).rglob('*')))

def get_valid_filename(name):
    """
    Document in django get vaild filename.
    """
    s = str(name).strip().replace(' ', '_')
    s = re.sub(r'(?u)[^-\w.]', '', s)
    if s in {'', '.', '..', '\\', '?', '|', ':' ,'/', '<', '>'}:
        raise SuspiciousFileOperation("Invaild file name: '%s'" % name)
    return s

class CreateToolTip(object):
    #create a tooltip for a given widget
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget ; self.text = text
        self.widget.bind("<Enter>", self.enter) ; self.widget.bind("<Leave>", self.leave) ; self.widget.bind("<ButtonPress>", self.leave)
        self.id = None ; self.tw = None
       
    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule() ; self.hidetip()

    def schedule(self):
        self.unschedule() ; self.id = self.widget.after(self.waittime, self.showtip)
        
    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0 ; x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25 ; y += self.widget.winfo_rooty() + 20
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw ; self.tw= None
        
        tw.destroy() if tw else 0
            
def convert_bytes(num):
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)