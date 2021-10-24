"""
	File Manager
	By NlogDev
	Based on v97's File manager with also can be seen here: https://github.com/v97/python-file-explorer
"""

#Note: Some sympol in here is not supported in your PC.
#📄 This is file sympol
#📁  This is folder sympol
#🖴 This is hard disk driver sympol

from threading import Thread
from tkinter import* ; from tkinter import simpledialog, messagebox, ttk ; import shutil ; import os, time; import errno
import function ; import tempfile
try:
	import win32api
except:
	messagebox.showerror("Error", "There is no module named 'win32api'. Please install it via 'pip install win32api' command'")
	
version = "1.4"

root = Tk()

clipBoard = [] ; tupleselect = () ; curdata = []
state = False ; transferMode = ''

fileListBox = None

curPathText = StringVar() ; pll = StringVar() #Adress text
curPathText.set(os.getcwd())

class OSPermissionError(Exception):
	pass

class OSFileNotFoundError(Exception):
	pass

#All control
def newFile(parent):
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			name = function.get_valid_filename(simpledialog.askstring("File Creator", "Please enter the file name:",parent=parent))
			print(name)
			if name == "None":
				return 'break'
			if(name == ("con", "nul", "aux", "...", "prn")):
				return 'break'
			if not os.path.isdir(name):
				try:
					f = open(name,"w+")
					f.write("")
					f.close()
				except Exception as e:
					raise Exception(e)
				reloadFiles()
				select(name)
		except function.SuspiciousFileOperation as e:
			messagebox.showerror("Error" , "Error: " + str(e))
			return 'break'


def newFolder(parent):
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			name = function.get_valid_filename(simpledialog.askstring("File Creator", "Please enter the folder name:",parent=parent))
			if name == "None":
				return 'break'
			if not os.path.exists(name):
				os.makedirs(name)
				reloadFiles()
				select(name)
			if(name == ("con", "nul", "aux", "...", "prn")):
				return 'break'
		except function.SuspiciousFileOperation as e:
			messagebox.showerror("Error", "Unable to create folder because: " + str(e))

def renameSelectedFile(event):
	if curPathText.get() == "System Directory":
		pass
	elif fileListBox.focus() == "":
		return 'break'
	else:
		try:
			fileName = curPathText.get() + "\\" + fileListBox.focus()
			in_ = function.get_valid_filename(simpledialog.askstring("File Creator", "New name:", parent=root))
			if in_ == "None":
				return 'break'
			if "." in in_:
				newName = curPathText.get() + "\\" + in_
				os.rename(fileName, newName)
				reloadFiles()
			if(in_ == ("con", "nul", "aux", "...", "prn")):
				return 'break'
		except function.SuspiciousFileOperation as e:
			messagebox.showerror(fileListBox.focus(), "Error: " + str(e))

def deleteSelectedFile(event):
	print(event)
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			fc = 0 ; multipleappname = fileListBox.selection()
			for c in multipleappname:
				fc += 1
			if fc == 0:
				pass
			else:
				confirmDelete = messagebox.askyesno("","Confirm to delete " + str(fc) + " File(s)?")
				if(confirmDelete):
					for f in multipleappname:
						try:
							shutil.rmtree(curPathText.get() + "\\" + f)
						except:
							try:
								os.remove(curPathText.get() + "\\" + f)
							except Exception as e:
								if fc == 1:
									messagebox.showerror("Error", e)
									return 'break'
								else:
									continuedel = messagebox.askyesno("Error","Error to delete '"+f+"'"+"\n\nError: "+str(e)+"\n\n Do you want to skip that file?")
									if(continuedel):
										continue
									else:
										break
						reloadFiles() ; print("Deleted " , f)
		except FileNotFoundError:
			reloadFiles()

def upward():
	curPathText.set(('\\').join(curPathText.get().split("\\")[:-1])) ; os.chdir("..")
	reloadFiles()

def copy(event):
	global clipBoard, transferMode, tupleselect
	clipBoard = [] ; tupleselect = () ; multiplefilename = fileListBox.selection()
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			for fn in multiplefilename:
				clipBoard.append(curPathText.get() + "\\" + str(fn))
				print("Added " + curPathText.get() + "\\" + str(fn) + " To clipboard.")
				print("Copied ", fn)
			transferMode = "copy" ; tupleselect = multiplefilename
		except TclError:
			pass

def cut(event):
	global clipBoard, transferMode, tupleselect
	multipleappname = fileListBox.selection()
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			clipBoard = [] ; tupleselect = () ; ex = 0
			transferMode = "cut"
			for a in multipleappname:
				ex += 1 ; clipBoard.append(curPathText.get() + "\\" + str(a))
				print("Added " + curPathText.get() + "\\" + str(a) + " To clipboard. (Transfermode = cut)")
				fileListBox.delete(a)
			tupleselect = multipleappname
		except TclError:
			pass

def paste(event):
	global clipBoard, transferMode, tupleselect
	try:
		if curPathText.get() == "System Directory":
			pass
		elif clipBoard == []:
			pass
		else:
			for fn in clipBoard:
				fileName = fn.split("\\")[-1] ; destination = curPathText.get() + "\\" + fileName
				try:
					if(transferMode == "cut"):
						shutil.move(fn, destination) ; notif = "Moving"
					elif(transferMode == "copy"):
						shutil.copyfile(fn, destination) ; notif = "Copying"
					print("Paste: ", notif + " " + fn + " to " + destination) ; reloadFiles() ; select(tupleselect)
				except Exception as e:
					continuepaste = messagebox.askyesno("Error","Error to paste '"+fn+"'"+"\n\nError: "+str(e)+"\n\n Do you want to skip that file?")
					if(continuepaste):
						continue
					else:
						break
			if transferMode == "cut":
				clipBoard = [] ; transferMode = "" ; reloadFiles()
	except Exception as e:
		if clipBoard == None:
			pass
		else:
			messagebox.showerror("Error!", "Error: " + str(e))
	

def check_for_updates():
	try:
		import requests
	except:
		return 'break'
	try:
		response = requests.get("https://api.github.com/repositories/398240683/releases/latest")
		checkversion = response.json()["tag_name"]
		if version == checkversion:
			messagebox.showinfo("Info", "You're installed the lastest update!")
		elif version >= checkversion:
			pass
		else:
			messagebox.showinfo("New Version!", "Your Current version is " + version +" Please update to new version: " + checkversion)
	except:
		messagebox.showerror("Error", "Please connect to the network")

def about():
	messagebox.showinfo("About", "File Manager " + version + "\n Made by LNogDEV.")

def menu_bar(root):
	menuBar = Menu(root)
	fileMenu = Menu(menuBar, tearoff=0)
	navMenu = Menu(menuBar, tearoff=0)
	viewMenu = Menu(menuBar, tearoff=0)
	helpMenu = Menu(menuBar, tearoff=0)
	fileMenu.add_command(label="New file", command=lambda: newFile(root))
	fileMenu.add_command(label="New folder", command=lambda: newFolder(root))
	fileMenu.add_command(label="Rename", command=lambda: renameSelectedFile(root), accelerator="F2")		
	fileMenu.add_command(label="Copy", command=copy, accelerator="Ctrl + C")	
	fileMenu.add_command(label="Cut", command=cut, accelerator="Ctrl + X")
	fileMenu.add_command(label="Paste", command=paste(root), accelerator="Ctrl + V")	
	fileMenu.add_command(label="Delete", command=lambda:deleteSelectedFile(root), accelerator="Del")
	fileMenu.add_separator()
	fileMenu.add_command(label="Exit", command=root.quit, accelerator="Alt + F4")

	navMenu.add_command(label="Refresh", command=reloadFiles)
	navMenu.add_command(label="Up", command=upward)
	navMenu.add_separator()
	navMenu.add_command(label="Open", command=lambda:opensystem(root))
	navMenu.add_separator()
	navMenu.add_command(label="Select all", command=lambda:select(fileListBox.get_children()), accelerator="Ctrl + A")
	navMenu.add_command(label="Select none", command=lambda:select(""))
	
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
	if errdir == '' or "System Directory":
		try:
			root.title("System Directory - File Manager") ; ChangeText("System Directory") ; curPathText.set("System Directory")
			dc = win32api.GetLogicalDriveStrings() ; drives = dc.split('\000')[:-1]
			fileListBox.delete(*fileListBox.get_children())
			count = 0
			for d in drives:
				fileListBox.insert("","end",iid=d ,values = ("🖴 " + d, "" , "Disk", "")) ; count += 1
			if count == 1 or 0:
				filecount.configure(text=str(count) + " item")
			else:
				filecount.configure(text=str(count) + " items")
		except:
			messagebox.showerror("Error", "Cannot collect the file list.")
	else:
		messagebox.showerror("Error", "Cannot read the folder.")	

def select(index):
	try:
		fileListBox.selection_set(index)
	except:
		pass

def reloadFiles():
	global transferMode
	selection = fileListBox.selection()
	fileListBox.delete(*fileListBox.get_children())
	try:
		flist = os.listdir(curPathText.get()) ; added = 0
		for ind, item in enumerate(flist):
			if function.file_size(item) is not None:
				name, extension = os.path.splitext(item)
				fileListBox.insert("","end",iid= item ,values = ("📄 " + item, time.ctime(os.path.getmtime(item)) , extension + " File" , function.file_size(item)))
			else:
				fileListBox.insert("","end",iid= item ,values = ("📁 " + item, time.ctime(os.path.getmtime(item)), "Directory" ,""))
			added += 1
		if added == 1 or 0:
			filecount.configure(text=str(added) + " item")
		else:
			filecount.configure(text=str(added) + " items")
		if transferMode == "cut":
			try:
				fileListBox.delete(*tupleselect)
			except:
				pass
		pl = os.getcwd()
		dirname = pl.split("\\")[-1]
		if dirname == "":
			dirname = pl
		ChangeText(pl)
		select(selection)
		root.title(dirname + "- File Manager")
		
	except (FileNotFoundError, UnboundLocalError):
		sysdir()

def openfunc():
	try:
		selection = fileListBox.selection() ; FName = fileListBox.focus()
		oldpath = os.getcwd() ; curPathText.set(oldpath) ; ChangeText(oldpath)
		if ":" in FName:
			curPathText.set(FName) ; os.chdir(FName)
			ChangeText(FName) ; reloadFiles()
		else:
			for f in selection:
				multiplefilePath = curPathText.get() + "\\" + str(f) ; os.startfile(multiplefilePath)
	except Exception as e:
		if e.errno == errno.ENOENT: 
			messagebox.showerror("An error occurred.", "Invaild file or directory name. Check the spelling and try again.")
		elif e.errno in [errno.EPERM, errno.EACCES]: 
			messagebox.showerror("An error occurred.", "You have no permisson to access.")
		else:
			print(e)

def opensystem(event):
	global curPathText
	global curdata
	FName = fileListBox.focus() ; s = fileListBox.selection()
	try:
		i = fileListBox.identify_row(event.y)
		if i in s:
			try:
				FPath = curPathText.get() + "\\" + FName
				try:
					curdata = []
					sv.set("")
					curPathText.set(FPath)
					os.chdir(FPath)
					ChangeText(FPath)
					reloadFiles()
				except: 
					openfunc()
			except Exception as e:
				if e.errno == errno.ENOENT: 
					messagebox.showerror("An error occurred.", "File Manager can't find '" + str(s) + "'. Check the spelling and try again.")
				elif e.errno in [errno.EPERM, errno.EACCES]: 
					messagebox.showerror("An error occurred.", "You have no permisson to access.")
				else:
					print(e)
		else:
			select("")
	except:
		openfunc()
	
def go(event):
	try:
		lastdir = os.getcwd()
		if "System Directory" == pll.get():
			sysdir()
		elif "" == pll.get():
			ChangeText(lastdir) ; curPathText.set(lastdir)
		elif "\\" not in pll.get():
			dir = pll.get() + "\\" ; curPathText.set(dir) ; os.chdir(dir) ; ChangeText(dir) ; reloadFiles()
		elif "maindir" == pll.get():
			sysdir()
		elif "." in pll.get():
			os.startfile(pll.get()) ; ChangeText(lastdir)
		else:
			curPathText.set(pll.get()) ; os.chdir(pll.get()) ; ChangeText(pll.get()) ; reloadFiles()
	except Exception as error:
		if error.errno == errno.ENOENT: 
			messagebox.showerror("An error occurred.", "File Manager can't find '" + pll.get() + "'. Check the spelling and try again.")
		elif error.errno in [errno.EPERM, errno.EACCES]: 
			messagebox.showerror("An error occurred.", "You have no permisson to acess this path.")
		elif error.args[0] != 123:
			messagebox.showerror("An error occurred.", "No path named: '" + pll.get() + "'. Check the spelling and try again.")
		else:
			print(error)
		
def showfileinfo():
	try:
		appname = fileListBox.selection()
		print(appname)
		window = Toplevel(root)		
		window.geometry("300x250")
		window.resizable(0,0)
		window.wm_attributes('-toolwindow', 'True')
		apptext = Label(window, text="...\n") ; typetext = Label(window, text="\nType of file: ...") ; sizetext = Label(window, text="Size: Calculating...")
		apptext.pack(side=TOP) ; typetext.pack(side=TOP) ; sizetext.pack(side=TOP)
		separator = Label (window, text=" ——————————————\n").pack(side=TOP)
		item = 0
		for fn in appname:
			item +=1
			name, extension = os.path.splitext(fn) ; curAppdir = curPathText.get() + "\\" + fn

		if item >= 2:
			print("Item is more than 2")
			window.destroy() if curPathText.get() =="System Directory" else 0
			window.title(str(item) + " files selected");apptext.configure(text=str(item)+" files selected") ; sizetext.configure(text="") ; typetext.configure(text="Type: Multiple types")
			return 'break'
		else:
			window.title(fn)
			try:
				if item >=2:
					raise Exception("Item is more than 2")
				elif item == 0:
					raise Exception("Item is 0.")
				else:
					print(item)
					ctime = Label(window, text="Created: "+time.ctime(os.path.getctime(fn)));mtime = Label(window, text="Modified: "+time.ctime(os.path.getmtime(fn))); atime = Label(window, text="Accessed: "+time.ctime(os.path.getatime(fn)))
					ctime.pack(side=TOP) ; mtime.pack(side=TOP) ; atime.pack(side=TOP)
				
			except:
				return 'break'
			try:
				try:
					apptext.configure(text=fn + "\n")
					typetext.configure(text="Type of file: '" + extension + "'")
					appsize = function.file_size(curAppdir)
					sizetext.configure(text="Size: " + appsize)
				except TypeError:
					if curPathText.get() == "System Directory":
						raise OSError("")
					else:
						typetext.configure(text="Type of file: Folder")
						size = function.get_folder_size(curAppdir)
						sizetext.configure(text="Size: " + str(size))
			except (OSError, PermissionError):
				if curPathText.get() == "System Directory":
					try:
						total, used, free = shutil.disk_usage(fn)
						sizetext.configure(text="Total: %d GB" % (total // (2**30)) + "\nUsed: %d GB" % (used // (2**30)) + "\nFree: %d GB" % (free // (2**30)))
						typetext.configure(text="Type: Disk")
					except:
						sizetext.configure(text="Cannot detect the size")
						typetext.configure(text="")
				else:
					sizetext.configure(text="Cannot detect the size")
					typetext.configure(text="")
	except:
		pass
def searchfunc(event):
	global curdata
	if curdata == []:
		curdata = fileListBox.get_children()
	else:
		pass
	value = sv.get()
	fileListBox.delete(*fileListBox.get_children())
	
	if value == '':
		reloadFiles()
		curdata = []
	else:
		filecount.configure(text="Search") ; data = [] ; root.title("Search Results")
		for item in curdata:
			if value in item.lower():
				data.append(item)
			else:
				pass
		for item in data:
			try:
				if curPathText.get() == "System Directory":
					fileListBox.insert("","end",iid=item ,values = ("🖴 " + item, "" , "Disk", ""))
				elif function.file_size(item) is not None:
					name, extension = os.path.splitext(item)
					fileListBox.insert("","end",iid= item ,values = ("📄 " + item, "" , extension + " File" , function.file_size(item)))
				else:
					fileListBox.insert("","end",iid= item ,values = ("📁 " + item, time.ctime(os.path.getmtime(item)), "Directory" ,""))
			except Exception as e:
				print("\a")
				print(e)

ChangeText = lambda text:pll.set(text)
#main file manager window
file_mgr = root

temppath = tempfile.gettempdir()
icon = (b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00h\x05\x00\x00'
		b'\x16\x00\x00\x00(\x00\x00\x00\x10\x00\x00\x00 \x00\x00\x00\x01\x00'
		b'\x08\x00\x00\x00\x00\x00@\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
		b'\x00\x01\x00\x00\x00\x01') + b'\x00'*1282 + b'\xff'*64
		

ICON_PATH = temppath + "\\icon.png"
try:
	f = open(ICON_PATH,"w+") ; f2 = open(ICON_PATH, "wb")
	f.write("") ; f2.write(icon)
	f.close() ; f2.close()
except:
	pass

root.after(2000, reloadFiles)

file_mgr.title("File Manager")
file_mgr.geometry("800x500")
file_mgr.minsize(700, 400)

try:
	root.iconbitmap(default=ICON_PATH)
except:
	pass

root.bind("<F11>", toggle_fullscreen)

frame1=Frame(root)
frame1.pack(side=TOP,fill=X)

toolbar=ttk.Frame(frame1)
toolbar.pack(side=TOP,fill=X)
upbtn = ttk.Button(frame1, text="↑", command=upward, width=4)
upbtntip = function.CreateToolTip(upbtn, "Up")
upbtn.pack(side=LEFT,padx=1)
refreshbtn = ttk.Button(frame1, text="↻", command=reloadFiles, width=4)
refreshbtntip = function.CreateToolTip(refreshbtn, "Refresh")
refreshbtn.pack(side=LEFT,padx=1)
sv = StringVar()
search = ttk.Entry(frame1,width=25, textvariable = sv)
search.pack(side=RIGHT, padx=2)
search.bind('<KeyRelease>', searchfunc)
gobtn = ttk.Button(frame1, text="↩", command=lambda:go(root), width=4)
gobtntp = function.CreateToolTip(gobtn, "Go to the path you typed in the adrress bar")
gobtn.pack(side=RIGHT, padx=4)

path = ttk.Entry(frame1,  textvariable = pll)
path.pack(side=LEFT, fill=BOTH, expand=1)

path.bind("<Return>", go)

m = PanedWindow(file_mgr,orient="horizontal")
m.pack(fill=BOTH ,expand=1)

frame2 = Frame(root)
frame2.pack(side=TOP,fill=X)

filecount = Label(frame2, text="Calculating...")
filecount.pack(side = LEFT)

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

scrollbar = Scrollbar(m)
scrollbar.pack(side = RIGHT, fill = BOTH)

fileListBox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = fileListBox.yview)

rightclick = Menu(root, tearoff = 0)
rightclick.add_command(label="Open", command=lambda:opensystem(root), font=('Segoe UI', 9, 'bold'))
rightclick.add_command(label ="Cut", command=cut(root))
rightclick.add_command(label ="Copy", command=copy(root))
rightclick.add_command(label ="Rename", command=lambda:renameSelectedFile(root))
rightclick.add_command(label="Delete", command=lambda:deleteSelectedFile(root))
rightclick.add_separator()
rightclick.add_command(label="Info", command=lambda:Thread(target=showfileinfo).start())

rc2 = Menu(root, tearoff= 0) #right click when the selection is nothing
rc2new = Menu(root, tearoff=0) ; rc2new.add_command(label="New folder", command=lambda:newFolder(root)), rc2new.add_command(label="New file", command=lambda:newFile(root))
rc2.add_command(label ="Paste", command=paste(root)) ; rc2.add_separator() ; rc2.add_cascade(label="New", menu=rc2new)
rc2.add_command(label ="Refresh", command=reloadFiles)

rc3 = Menu(root, tearoff=0) #System Directory right click
rc3.add_command(label="Open", command=lambda:opensystem(root), font=('Segoe UI', 9, 'bold')) ; rc3.add_separator() ; rc3.add_command(label="Info", command=showfileinfo)

def checkselect(event):
	try:
		count = 0
		for c in fileListBox.selection():
			count +=1
		if count >=2:
			return 'break'
		else:
			select(fileListBox.identify_row(event.y))
	except Exception as e:
		print(e)

def do_popup(event):
	checkclipboard() ; checkselect(event)
	if fileListBox.selection() == ():
		try:
			rc2.tk_popup(event.x_root, event.y_root)
		finally:
			rc2.grab_release()
	elif curPathText.get() == "System Directory":
		try:
			rc3.tk_popup(event.x_root, event.y_root)
		finally:
			rc3.grab_release()
	else:
		try:
			rightclick.tk_popup(event.x_root, event.y_root)
		finally:
			rightclick.grab_release()

def checkclipboard():
	if clipBoard == []:
		rc2.entryconfig("Paste", state="disabled")
	else:
		rc2.entryconfig("Paste", state="normal")

fileListBox.bind("<Button-3>", do_popup) ; fileListBox.bind('<<ListboxSelect>>') ; fileListBox.bind("<Double-Button-1>", opensystem)
fileListBox.bind("<Delete>", deleteSelectedFile) ; fileListBox.bind("<Control-c>", copy) ; fileListBox.bind("<Control-x>", cut)
root.bind("<F2>", renameSelectedFile) ; root.bind("<Control-v>", paste)

reloadFiles()

m.add(fileListBox) ; menu_bar(file_mgr)

if(__name__ == "__main__"):
	root.mainloop()
