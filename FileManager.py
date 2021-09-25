"""
	File Manager
	By NlogDev
"""


from tkinter import *
from tkinter import simpledialog, messagebox, ttk
import shutil        
import os,  time
try:
	import django
	from django.utils.text import get_valid_filename
except ImportError:
	messagebox.showerror("Error", "Please intall django module.")
	os.system("pip install django")
from pathlib import Path
import win32api

version = "1.3.1"

root = Tk()

clipBoard = []

state = False
cutprocess = True

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
    for x in ['B', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
def file_size(file_path):
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

#All control
#WARN: NO multiple selection.
def newFile(parent):
	if curPathText.get() == "System Directory":
		pass
	else:
		name = get_valid_filename(simpledialog.askstring("Input", "Please enter the file name:",
									parent=parent))
		if(name is None):
			pass
		if(name == "con"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
		if(name == "nul"):
			messagebox.showwarning("Error", "The specified device name is invaild.")
		try:
			f = open(name,"w+")
			f.write("")
			f.close()
		except Exception as e:
			messagebox.showerror(f , "Error: " + str(e))
		reloadFiles(name)

def newFolder(parent):
	if curPathText.get() == "System Directory":
		pass
	else:
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
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			fileName = curPathText.get() + "\\" + fileListBox.focus()
			in_ = get_valid_filename(simpledialog.askstring("Input", "Please enter the new file name: \n *Note: You Can't rename multiple files*", parent=parent))
			if(in_ is None):
				pass
			if "." in in_:
				newName = curPathText.get() + "\\" + in_
				os.rename(fileName, newName)
				reloadFiles()
			if(in_ == "con"):
				pass
			if(in_ == "nul"):
				pass
		except django.core.exceptions.SuspiciousFileOperation as e:
			messagebox.showerror(fileListBox.focus(), "Error: " + str(e))

def deleteSelectedFile():
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			ex = 0
			multipleappname = fileListBox.selection()
			for count in multipleappname:
				ex += 1
				
			confirmDelete = messagebox.askyesno("","Confirm to delete " + str(ex) + " Files?")
			if(confirmDelete):
				for filee in multipleappname:
					os.remove(curPathText.get() + "\\" + filee)
					reloadFiles(0)
		except (TclError, PermissionError) as e:
			messagebox.showerror("Error to delete '" + fileListBox.selection() + "'", "Error: " + str(e))

def upward():
	curPathText.set(('\\').join(curPathText.get().split("\\")[:-1]))
	os.chdir("..")
	reloadFiles()

#Copy/Cut/Paste function
#WARN: NO multiple selection.
def copy():
	global clipBoard
	global transferMode
	clipBoard = [] #Make sure to clear the Clipboard
	multiplefilename = fileListBox.selection()
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			for fn in multiplefilename:
				clipBoard.append(curPathText.get() + "\\" + str(fn))
				print("Added " + curPathText.get() + "\\" + str(fn) + "To clipboard.")
				print("Copied", fn)
			transferMode = "copy"
		except TclError:
			pass

def cut():
	global clipBoard
	global transferMode
	multipleappname = fileListBox.selection()
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			#Make sure to clear the clipboard
			clipBoard = []
			ex = 0
			transferMode = "cut"
			for a in multipleappname:
				ex += 1
				clipBoard.append(curPathText.get() + "\\" + str(a))
				print("Added " + curPathText.get() + "\\" + str(a) + "To clipboard.")
				fileListBox.delete(a)
				print("Cut", a)
		except TclError:
			pass

def paste():
	global clipBoard
	global transferMode
	global cutprocess
	try:
		if curPathText.get() == "System Directory":
			pass
		else:
			for fn in clipBoard:
				fileName = fn.split("\\")[-1]
				destination = curPathText.get() + "\\" + fileName
				if fn == destination:
					pass
				else:
					if(transferMode == "cut"):
						cutprocess = True
						shutil.move(fn, destination)
						notif = "Moving"
					elif(transferMode == "copy"):
						shutil.copyfile(fn, destination)
						notif = "Copying"
					print("Paste", notif + " " + fn + " to " + destination)
			if notif == "Moving":
				clipBoard = []
				cutprocess = False
	except Exception as e:
		if clipBoard == None:
			pass
		else:
			messagebox.showerror(clipBoard, "Error: " + str(e))
	reloadFiles(0)

def check_for_updates():
	try:
		import requests
	except:
		pass
	try:
		response = requests.get("https://api.github.com/repositories/398240683/releases/latest")
		checkversion = response.json()["tag_name"]
		if version == checkversion:
			messagebox.showinfo("Info", "You're installed the lastest update!")
		elif version >= checkversion:
			messagebox.showwarning("Um...", "That is a ... future version?")
		else:
			messagebox.showinfo("New Version!", "Your Current version is " + version +" Please update to new version: " + checkversion)
	except:
		messagebox.showerror("Error", "Please connect to the network")

def about():
	messagebox.showinfo("About", "📁 File Manager " + version + "\n Made by LNogDEV.")

def menu_bar(root):
	menuBar = Menu(root)
	fileMenu = Menu(menuBar, tearoff=0)
	navMenu = Menu(menuBar, tearoff=0)
	viewMenu = Menu(menuBar, tearoff=0)
	helpMenu = Menu(menuBar, tearoff=0)
	fileMenu.add_command(label="New file", command=lambda: newFile(root))
	fileMenu.add_command(label="New folder", command=lambda: newFolder(root))
	fileMenu.add_command(label="Rename", command=lambda: renameSelectedFile(root))		
	fileMenu.add_command(label="Copy", command=copy)	
	fileMenu.add_command(label="Cut", command=cut)
	fileMenu.add_command(label="Paste", command=paste)	
	fileMenu.add_command(label="Delete", command=deleteSelectedFile)
	fileMenu.add_separator()
	fileMenu.add_command(label="Exit", command=root.quit, accelerator="Alt + F4")

	navMenu.add_command(label="Refresh", command=reloadFiles)
	navMenu.add_command(label="Up", command=upward)
	navMenu.add_separator()
	navMenu.add_command(label="Open", command=opensystem)
	
	viewMenu.add_command(label="Toggle fullscreen", command=toggle_fullscreen, accelerator="F11")

	helpMenu.add_command(label="Check for updates", command=check_for_updates)
	helpMenu.add_command(label="About", command=about)

	menuBar.add_cascade(label="File", menu=fileMenu)
	menuBar.add_cascade(label="Nav", menu=navMenu)
	menuBar.add_cascade(label="View", menu=viewMenu)
	menuBar.add_cascade(label="Help", menu=helpMenu)
	root.config(menu=menuBar)

def toggle_fullscreen(event=None):
    global state
    state = not state
    root.attributes("-fullscreen", state)

def sysdir():
	errdir = curPathText.get()
	if errdir == '' or "System Directory" and "maindir":
		try:
			ChangeText("System Directory")
			curPathText.set("System Directory")
			drives = win32api.GetLogicalDriveStrings()
			drives = drives.split('\000')[:-1]
			fileListBox.delete(*fileListBox.get_children())
			for d in drives:
				fileListBox.insert("","end",iid=d ,values = (d, "" , "Local Disk", ""))
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
				fileListBox.insert("","end",iid= item ,values = (item, time.ctime(os.path.getmtime(item)) , extension + " File" , file_size(item)))
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
	fileName = fileListBox.focus()
	multiplefile = fileListBox.selection()
	try:
		filePath = curPathText.get() + "\\" + fileName
		if ":" in fileName:
			curPathText.set(fileName)
			os.chdir(fileName)
			ChangeText(fileName)
			reloadFiles()
		else:
			try:
				curPathText.set(filePath)
				os.chdir(filePath)
				ChangeText(filePath)
				reloadFiles()
			except OSError:
				try:
					curPathText.set(oldpath)
					ChangeText(oldpath)
					for f in multiplefile:
						multiplefilePath = curPathText.get() + "\\" + str(f)
						os.startfile(multiplefilePath)
				except OSError:
					messagebox.showerror("Error", "Unable to enter folder or run file named: " + fileName)
	except Exception as e:
		if pll.get() == "System Directory":
			messagebox.showerror("Unable to get access from '" + fileName + "'", "Error: Please insert a disc into the Drive.")
		else:
			messagebox.showerror("Unable to get access from '" + fileName + "'", "Error: " + str(e))

def go(event):
	try:
		lastdir = os.getcwd()
		if "System Directory" == pll.get():
			sysdir()
		elif "maindir" == pll.get():
			sysdir()
		elif "\\" not in pll.get():
			ChangeText(lastdir)
		elif "." in pll.get():
			os.startfile(pll.get)
			ChangeText(lastdir)
		else:
			curPathText.set(pll.get())
			os.chdir(pll.get())
			ChangeText(pll.get())
			reloadFiles()
	except (OSError, TypeError):
		messagebox.showerror("An error occurred.", "File Manager can't find '" + pll.get() + "'. Check the spelling and try again.")
		
def showfileinfo():
	appName = fileListBox.focus()
	multipleappname = fileListBox.selection()
	window = Toplevel(root)
	window.title(appName)
	window.geometry("300x250")
	window.resizable(0,0)
	curAppdir = curPathText.get() + "\\" + appName
	apptext = Label(window, text="📁 " + appName + "\n")
	apptext.pack(side=TOP)
	typetext = Label(window, text="\nType of file: ")
	typetext.pack(side=TOP)
	sizetext = Label(window, text="Size: ")
	sizetext.pack(side=TOP)
	separator = Label (window, text=" ——————————————\n")
	separator.pack(side=TOP)
	ex = 0
	name, extension = os.path.splitext(appName)
	try:
		try:
			appsize = file_size(curAppdir)
			sizetext.configure(text="Size: " + appsize)
			typetext.configure(text="Type of file: '" + extension + "'")
		except TypeError:
			if curPathText.get() == "System Directory":
				raise OSError("")
			else:
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
	
	for count in multipleappname:
		ex += 1
		if ex >= 1:
			window.title(str(ex) + " files selected")
			apptext.configure(text=str(ex) + " files selected")
			sizetext.configure(text="")
			typetext.configure(text="Type: Multiple types")

	try:
		try:
			if ex >= 1:
				pass
			else:
				ctime = Label(window, text="Created: %s" % time.ctime(os.path.getctime(appName)))
				ctime.pack(side=TOP)
				mtime = Label(window, text="Modified: %s" % time.ctime(os.path.getmtime(appName)))
				mtime.pack(side=TOP)
				atime = Label(window, text="Accessed: %s" % time.ctime(os.path.getatime(appName)))
				atime.pack(side=TOP)
		except PermissionError:
			pass
	except FileNotFoundError:
		pass

frame1=Frame(root)
frame1.pack(side=TOP,fill=X)

file_mgr = root
root.after(20000, reloadFiles)

file_mgr.title("File Manager")
file_mgr.geometry("800x500")

root.bind("<F11>", toggle_fullscreen)

toolbar=ttk.Frame(frame1)
toolbar.pack(side=TOP,fill=X)
upbtn = ttk.Button(frame1, text="↑", command=upward, width=5)
upbtn.pack(side=LEFT,padx=1)
refreshbtn = ttk.Button(frame1, text="↻", command=reloadFiles, width=5)
refreshbtn.pack(side=LEFT,padx=1)
newfolderbtn = ttk.Button(frame1, text="+📁", command=lambda: newFolder(root), width=5)
newfolderbtn.pack(side=RIGHT, padx=1)
newfilebtn = ttk.Button(frame1, text="+File", command=lambda: newFile(root), width=5)
newfilebtn.pack(side=RIGHT, padx=1)
gobtn = ttk.Button(frame1, text="↩", command=lambda:go(root), width=5)
gobtn.pack(side=RIGHT, padx=4)

def ChangeText(text):
	pll.set(text)

pll = StringVar()
path = ttk.Entry(frame1,  textvariable = pll)
path.pack(side=LEFT, fill=BOTH, expand=1)

path.bind("<Return>", go)

m = PanedWindow(file_mgr,orient="horizontal")
m.pack(fill=BOTH ,expand=1)

fileListBox = ttk.Treeview(m, name='fileListBox')
fileListBox['columns']=('name', 'datem', 'type', 'size')
fileListBox.column('#0', width=0, stretch=NO)
fileListBox.column('name',  width=80)
fileListBox.column('datem',  width=80)
fileListBox.column('type',  width=80)
fileListBox.column('size',  width=80)

fileListBox.heading('#0')
fileListBox.heading('name', text='Name')
fileListBox.heading('datem', text='Date modified')
fileListBox.heading('type', text='Type')
fileListBox.heading('size', text='Size')

fileListBox.bind('<<ListboxSelect>>')
fileListBox.bind("<Double-Button-1>", opensystem)
fileListBox.bind('<Control-Key-C>', copy)
fileListBox.bind('<Control-Key-V>', paste)

scrollbar = Scrollbar(m)
scrollbar.pack(side = RIGHT, fill = BOTH)

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
