from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
import shutil         
import os, re, time
from django.utils.text import get_valid_filename
import django
from pathlib import Path
import shutil
from tkinter import ttk

version = "1.3"

    
root = Tk()

clipBoard = None

fileListBox = None
textArea = None

curPathText = StringVar()
curPathText.set(os.getcwd())


def get_folder_size(folder):
    return ByteSize(sum(file.stat().st_size for file in Path(folder).rglob('*')))


class ByteSize(int):

    _KB = 1024
    _suffixes = 'B', 'KB', 'MB', 'GB'

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.bytes = self.B = int(self)
        self.kilobytes = self.KB = self / self._KB**1
        self.megabytes = self.MB = self / self._KB**2
        self.gigabytes = self.GB = self / self._KB**3
        self.petabytes = self.PB = self / self._KB**4
        *suffixes, last = self._suffixes
        suffix = next((
            suffix
            for suffix in suffixes
            if 1 < getattr(self, suffix) < self._KB
        ), last)
        self.readable = suffix, getattr(self, suffix)

        super().__init__()

    def __str__(self):
        return self.__format__('.2f')

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, super().__repr__())

    def __format__(self, format_spec):
        suffix, val = self.readable
        return '{val:{fmt}} {suf}'.format(val=val, fmt=format_spec, suf=suffix)

    def __sub__(self, other):
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        return self.__class__(super().__add__(other))

    def __mul__(self, other):
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        return self.__class__(super().__sub__(other))

    def __radd__(self, other):
        return self.__class__(super().__add__(other))

    def __rmul__(self, other):
        return self.__class__(super().__rmul__(other))   

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)


def newFile(parent):
	name = get_valid_filename(simpledialog.askstring("Input", "Please enter the file name:",
                                parent=parent))
	if(name is None):
		pass
	if(name == "con"):
		messagebox.showwarning("Error", "The specified device name is invaild.")
	if(name == "nul"):
		messagebox.showwarning("Error", "The specified device name is invaild.")
	f = open(name,"w+")
	f.write("")
	f.close()
	reloadFiles(name)

def newFolder(parent):
	try:
		name = get_valid_filename(simpledialog.askstring("Input", "Please enter the file name:",
									parent=parent))
		if(name is None):
			pass
		if not os.path.exists(name):
			os.makedirs(name)
		if(name == "con"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
		if(name == "nul"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
	except django.core.exceptions.SuspiciousFileOperation as e:
		messagebox.showerror("Error", "Unable to create folder because: " + str(e))
def renameSelectedFile(parent):
	try:
		fileName = curPathText.get() + "\\" + fileListBox.focus()
		in_ = get_valid_filename(simpledialog.askstring("Input", "Please enter the new file name:", parent=parent))
		if(in_ is None):
			pass
		if "." in in_:
			newName = curPathText.get() + "\\" + in_
			os.rename(fileName, newName)
			reloadFiles(newName)
		if(in_ == "con"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
		if(in_ == "nul"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
	except django.core.exceptions.SuspiciousFileOperation as e:
		messagebox.showerror("Error", "Unable to rename that file because: " + str(e))
def deleteSelectedFile():
	try:
		fileName = fileListBox.focus()
		confirmDelete = messagebox.askokcancel("","Confirm to delete " + fileName + "?")
		if(confirmDelete):
			os.remove(curPathText.get() + "\\" + fileName)
			reloadFiles(0)
	except (TclError, PermissionError) as e:
		messagebox.showerror("Error to delete '" + (fileName) + "'", "Error: " + str(e))


def upward():
	curPathText.set(('\\').join(curPathText.get().split("\\")[:-1]))
	os.chdir("..")
	reloadFiles()

def copy():
	global clipBoard
	global transferMode
	try:
		clipBoard = curPathText.get() + "\\" + fileListBox.focus()
		transferMode = "copy"
		print("Copied", clipBoard)
	except TclError:
		pass

def cut():
	global clipBoard
	global transferMode
	try:
		clipBoard = curPathText.get() + "\\" + fileListBox.focus()
		transferMode = "cut"
		print("Cut", clipBoard)
	except TclError:
		pass
def check_for_updates():
	import requests
	try:
		response = requests.get("https://api.github.com/repositories/398240683/releases/latest")
		checkversion = response.json()["tag_name"]
		if version == checkversion:
			messagebox.showinfo("Info", "You're installed the lastest update!")
		elif version >= checkversion:
			messagebox.showwarning("Um...", "That is a ... future version?")
		else:
			messagebox.showinfo("New Version!", "Your Current version is" + version +" Please update to new version: " + checkversion)
	except:
		messagebox.showerror("Error", "Please connect to the network")

def paste():
	global clipBoard
	global transferMode
	try:
		fileName = clipBoard.split("\\")[-1]
		try:
			if(transferMode == "copy"):
				[fileName, fileType] = fileName.split(".")
				fileName = fileName + "_copy." + fileType
		except:
			pass
		destination = curPathText.get() + "\\" + fileName
		if(transferMode == "cut"):
			shutil.move(clipBoard, destination)
			notif = "Moving"
		elif(transferMode == "copy"):
			shutil.copyfile(clipBoard, destination)
			notif = "Copying"
		messagebox.showinfo("Paste", notif + " " + clipBoard + " to " + destination)
	except AttributeError:
		pass
	reloadFiles(clipBoard)

def about():
	messagebox.showinfo("About", "📁 File Manager " + version + "\n Made by LNogDEV.")

def menu_bar(root):
	menuBar = Menu(root)
	fileMenu = Menu(menuBar, tearoff=0)
	navMenu = Menu(menuBar, tearoff=0)
	helpMenu = Menu(menuBar, tearoff=0)
	fileMenu.add_command(label="New file", command=lambda: newFile(root))
	fileMenu.add_command(label="New folder", command=lambda: newFolder(root))
	fileMenu.add_command(label="Rename", command=lambda: renameSelectedFile(root))		
	fileMenu.add_command(label="Copy", command=copy)	
	fileMenu.add_command(label="Cut", command=cut)
	fileMenu.add_command(label="Paste", command=paste)	
	fileMenu.add_command(label="Delete", command=deleteSelectedFile)
	fileMenu.add_separator()
	fileMenu.add_command(label="Exit", command=root.quit)

	navMenu.add_command(label="Refresh", command=reloadFiles)
	navMenu.add_command(label="Open", command=opensystem)
	navMenu.add_command(label="Up", command=upward)

	helpMenu.add_command(label="Check for updates", command=check_for_updates)
	helpMenu.add_command(label="About", command=about)

	menuBar.add_cascade(label="File", menu=fileMenu)
	menuBar.add_cascade(label="Nav", menu=navMenu)
	menuBar.add_cascade(label="Help", menu=helpMenu)
	root.config(menu=menuBar)

def sysdir():
	errdir = curPathText.get()
	if errdir == '' or "System Directory":
		try:
			ChangeText("System Directory")
			disk = re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)
			fileListBox.delete(*fileListBox.get_children())
			for f in disk:
				fileListBox.insert("","end",iid= f ,values = (f, "" , "Disk", ""))
		except:
			messagebox.showerror("Error", "Cannot collect the file list.")
	else:
		messagebox.showerror("Error", "Cannot read the folder.")	

def reloadFiles(fileToSelect = None):
	fileListBox.delete(*fileListBox.get_children())
	try:
		flist = os.listdir(curPathText.get())
		added = 0
		for ind, item in enumerate(flist):
			if(not (fileToSelect is None)):
				if(fileToSelect == item):
					selectionInd = added
			if file_size(item) is not None:
				name, extension = os.path.splitext(item)
				fileListBox.insert("","end",iid= item ,values = (item, file_size(item), extension + " File" ,time.ctime(os.path.getmtime(item))))
			else:
				fileListBox.insert("","end",iid= item ,values = (item, "", "Directory" ,time.ctime(os.path.getmtime(item))))
			added += 1
		pl = os.getcwd()
		ChangeText(pl)
	except (FileNotFoundError, UnboundLocalError):
		sysdir()

def opensystem(event):
	global curPathText
	oldpath = os.getcwd()
	folderName = fileListBox.focus()
	try:
		newPath = curPathText.get() + "\\" + folderName
		if ":" in folderName:
			curPathText.set(folderName)
			os.chdir(folderName)
			ChangeText(folderName)
			reloadFiles()
		else:
			try:
				curPathText.set(newPath)
				os.chdir(newPath)
				ChangeText(newPath)
				reloadFiles()
			except OSError:
				try:
					curPathText.set(oldpath)
					os.startfile(newPath)
				except OSError:
					messagebox.showerror("Error", "Unable to enter folder or run file named: " + folderName)
	except:
		messagebox.showerror("Error", "Unable to get access from '" + folderName + "'")

def go(event):
	try:
		lastdir = os.getcwd()
		if "System Directory" == pll.get():
			sysdir()
		else:
			try:
				os.startfile(pll.get())
				ChangeText(lastdir)
			except OSError:
				os.chdir(pll.get())
				ChangeText(pll.get())
				reloadFiles()
	except (OSError, TypeError):
		messagebox.showerror("an error occurred.", "File Manager can't find '" + pll.get() + "'. Check the spelling and try again.")
		curPathText.set(lastdir)
		ChangeText(lastdir)
		os.chdir(lastdir)

def showfileinfo():
	appName = fileListBox.focus()
	name, extension = os.path.splitext(appName)
	curAppdir = curPathText.get() + "\\" + appName
	window = Toplevel(root)
	window.title(appName)
	window.geometry("300x200")
	window.resizable(0,0)
	apptext = Label(window, text="📁 " + appName + "\n")
	apptext.pack(side=TOP)
	typetext = Label(window, text="\nType of file: ")
	typetext.pack(side=TOP)
	sizetext = Label(window, text="Size: ")
	sizetext.pack(side=TOP)
	separator = Label (window, text=" ——————————————\n")
	separator.pack(side=TOP)

	try:
		try:
			appsize = file_size(curAppdir)
			sizetext.configure(text="Size: " + appsize)
			typetext.configure(text="Type of file: '" + extension + "'")
		except TypeError:
			size = get_folder_size(curAppdir)
			sizetext.configure(text="Size: " + str(size))
			typetext.configure(text="Type of file: Folder")
	except (OSError, PermissionError):
		try:
			total, used, free = shutil.disk_usage(appName)

			sizetext.configure(text="Total: %d GB" % (total // (2**30)) + "\nUsed: %d GB" % (used // (2**30)) + "\nFree: %d GB" % (free // (2**30)))
			typetext.configure(text="Type: Local Disk")
		except (OSError, PermissionError, TclError):
			sizetext.configure(text="Cannot detect the size")
			typetext.configure(text="")

	try:
		try:
			ctime = Label(window, text="Created: %s" % time.ctime(os.path.getctime(appName)))
			ctime.pack(side=TOP)
			mtime = Label(window, text="Modified: %s" % time.ctime(os.path.getmtime(appName)))
			mtime.pack(side=TOP)
			atime = Label(window, text="Accessed: %s" % time.ctime(os.path.getatime(appName)))
			atime.pack(side=TOP)
		except PermissionError:
			pass
	except FileNotFoundError:
		window.destroy()
		messagebox.showwarning("Warning", "Please select a file to show that file info.")

	
	
frame1=Frame(root)
frame1.pack(side=TOP,fill=X)

file_mgr = root
file_mgr.title("File Manager")
file_mgr.geometry("800x500")
	
toolbar=Frame(frame1)
toolbar.pack(side=TOP,fill=X)
upbtn = Button(frame1, text="↑ Up", command=upward)
upbtn.pack(side=LEFT,padx=1)
refreshbtn = Button(frame1, text="↻ Refresh", command=reloadFiles)
refreshbtn.pack(side=LEFT,padx=1)
newfolderbtn = Button(frame1, text="New 📁", command=lambda: newFolder(root))
newfolderbtn.pack(side=RIGHT, padx=1)
newfilebtn = Button(frame1, text="+File", command=lambda: newFile(root))
newfilebtn.pack(side=RIGHT, padx=1)
delfilebtn = Button(frame1, text="✖ Delete", command=deleteSelectedFile)
delfilebtn.pack(side=RIGHT, padx=1)
copybtn = Button(frame1, text="Copy", command=copy)
copybtn.pack(side=RIGHT, padx=1)
cutbtn = Button(frame1, text="✂Cut", command=cut)
cutbtn.pack(side=RIGHT, padx=1)
pastebtn = Button(frame1, text="Paste", command=paste)
pastebtn.pack(side=RIGHT, padx=1)
gobtn = Button(frame1, text="↩Go", command=lambda:go(root))
gobtn.pack(side=RIGHT, padx=4)
def ChangeText(text):
	pll.set(text)

pll = StringVar()
path = Entry(frame1,  textvariable = pll)
path.pack(side=LEFT, fill=BOTH, expand=1)

path.bind("<Return>", go)

m = PanedWindow(file_mgr,orient="horizontal")
m.pack(fill=BOTH ,expand=1)

fileListBox = ttk.Treeview(m, name='fileListBox')
fileListBox['columns']=('name', 'size', 'type', 'datem')
fileListBox.column('#0', width=0, stretch=NO)
fileListBox.column('name',  width=80)
fileListBox.column('size',  width=80)
fileListBox.column('datem',  width=80)
fileListBox.column('type',  width=80)

fileListBox.heading('#0')
fileListBox.heading('name', text='Name')
fileListBox.heading('size', text='Size')
fileListBox.heading('datem', text='Date modified')
fileListBox.heading('type', text='Type')

fileListBox.bind('<<ListboxSelect>>')
fileListBox.bind("<Double-Button-1>", opensystem)
fileListBox.bind('<Control-Key-C>', copy)
fileListBox.bind('<Control-Key-V>', paste)
scrollbar = Scrollbar(m)
scrollbar.pack(side = RIGHT, fill = BOTH)

for values in range(-1):
	fileListBox.insert(END, values)

fileListBox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = fileListBox.yview)

rightclick = Menu(root, tearoff = 0)
rightclick.add_command(label="Open", command=lambda:opensystem(root))
rightclick.add_command(label ="Cut", command=cut)
rightclick.add_command(label ="Copy", command=copy)
rightclick.add_command(label ="Paste", command=paste)
rightclick.add_command(label ="Rename", command=lambda:renameSelectedFile(root))
rightclick.add_command(label="Delete", command=deleteSelectedFile)
rightclick.add_separator()
rightclick.add_command(label ="Refresh", command=reloadFiles)
rightclick.add_command(label="Info", command=showfileinfo)
def do_popup(event):
	try:
		rightclick.tk_popup(event.x_root, event.y_root)
	finally:
		rightclick.grab_release()

fileListBox.bind("<Button-3>", do_popup)

reloadFiles()

m.add(fileListBox)

menu_bar(file_mgr)

if(__name__ == "__main__"):
	root.mainloop()
