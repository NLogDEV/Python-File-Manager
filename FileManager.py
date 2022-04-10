"""
	File Manager
	By NlogDev
"""

#Note: Some sympol in here is not supported in your PC.
#📄 This is file sympol
#📁  This is folder sympol
from threading import Thread
from tkinter import* ; from tkinter import simpledialog, messagebox, ttk ; import shutil ; import os, time; import errno;import subprocess, sys
import function ; import tempfile
try:
	import win32api
	splash = "\\"
except:
	if 'nt' in os.name:
		messagebox.showerror("Error", "There is no module named 'win32api'. Please install it via 'pip install win32api' command'")
	else:
		linux = True
		splash = "/"
	
version="1.5"

root = Tk()

clipBoard=[];tupleselect=();curdata=[];bck=[];frwd=[];items=0;stoprefresh=False
state=False;transferMode='';search=False

fileListBox = None

curPathText = StringVar() ; pll = StringVar() #Adress text
curPathText.set(os.getcwd())

#All control
def newFile(parent):
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			name = function.get_valid_filename(simpledialog.askstring("File Creator", "Please enter the file name:",parent=parent))
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
			return 'break' if(name == ("con", "nul", "aux", "...", "prn")) else 0
		except (function.SuspiciousFileOperation, NotADirectoryError) as e:
			messagebox.showerror("Error", "" + str(e))

def renameSelectedFile(event):
	if curPathText.get() == "System Directory":
		pass
	else:
		try:
			fileName = curPathText.get() + splash + fileListBox.focus()
			in_ = function.get_valid_filename(simpledialog.askstring("File Creator", "New name:", parent=root))
			if in_ == "None":
				return 'break'
			if "." in in_:
				newName = curPathText.get() + "\\" + in_
				os.rename(fileName, newName)
				reloadFiles()
			return 'break' if(in_ == ("con", "nul", "aux", "...", "prn")) else 0
		except function.SuspiciousFileOperation as e:
			messagebox.showerror(fileListBox.focus(), "Error: " + str(e))

def deleteSelectedFile(event):
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
							shutil.rmtree(curPathText.get() + splash + f)
							fc-=1
						except:
							try:
								os.remove(curPathText.get() + splash + f)
								fc-=1
							except Exception as e:
								if fc == 1:
									messagebox.showerror("Error", e)
									return 'break'
								else:
									continuedel = messagebox.askyesno("Error","Error to delete '"+f+"'"+"\n\nError: "+str(e)+"\n\nSkip the file?")
									if(continuedel):
										continue
									else:
										break
						reloadFiles() ; print("Deleted: ",f)
		except FileNotFoundError:
			reloadFiles()

def upward():
	global stoprefresh	
	lastdir = os.getcwd()
	bck.append(lastdir);stoprefresh=False
	curPathText.set((str(splash)).join(curPathText.get().split(str(splash))[:-1]));os.chdir("..");reloadFiles()
	if curPathText.get() == "System Directory":
		upbtn.configure(state=DISABLED);bck.append("System Directory") 
	else:
		pass
	

def copy(event):
	global clipBoard, transferMode, tupleselect
	clipBoard = [] ; tupleselect = () ; multiplefilename = fileListBox.selection()
	if curPathText.get() == "System Directory":
		0
	else:
		try:
			for fn in multiplefilename:
				clipBoard.append(curPathText.get() + "\\" + str(fn))
			transferMode = "copy" ; tupleselect = multiplefilename
		except TclError as e:
			print("ERROR: ", e)

def cut(event):
	global clipBoard, transferMode, tupleselect
	multipleappname = fileListBox.selection()
	if curPathText.get() == "System Directory":
		0
	else:
		try:
			clipBoard = [] ; tupleselect = () ; ex = 0
			transferMode = "cut"
			for a in multipleappname:
				ex += 1 ; clipBoard.append(curPathText.get() + "\\" + str(a));fileListBox.delete(a)
			tupleselect = multipleappname
		except TclError as e:
			print("ERROR: ", e)

def paste(event):
	global clipBoard, transferMode, tupleselect
	totalfiles = 0;pastedfiles = 0
	pw = Toplevel(root) ; pw.title("File Operation");pw.geometry("800x200");pw.resizable(0,0)
	counter = Label(pw, text=".../...") ; fnc = Label(pw, text="...");counter.pack(); fnc.pack()
	try:
		if curPathText.get() == "System Directory":
			pw.destroy()
		elif clipBoard == []:
			pw.destroy()
		else:
			for f in clipBoard:
				totalfiles +=1
			for fn in clipBoard:
				fileName = fn.split(splash)[-1];destination=curPathText.get()+"\\"+fileName
				try:
					if(transferMode == "cut"):
						notif ="Moving ";pastedfiles +=1;fnc.configure(text=fileName);fnctip = function.CreateToolTip(fnc, fn)
						counter.configure(text=notif+str(pastedfiles)+"/"+str(totalfiles)+" files.")
						shutil.move(fn, destination)
					elif(transferMode == "copy"):
						pastedfiles +=1; notif = "Copying";fnc.configure(text=fileName);fnctip = function.CreateToolTip(fnc, fn)
						counter.configure(text=notif+str(pastedfiles)+"/"+str(totalfiles)+" files.")
						shutil.copyfile(fn, destination)
					print("Paste: ", notif +" "+fn +" to "+destination);reloadFiles();select(tupleselect)
				except Exception as e:
					continuepaste = messagebox.askyesno("Error","Error to paste '"+fn+"'"+"\n\nError: "+str(e)+"\n\n Do you want to skip the file?")
					if(continuepaste):
						continue
					else:
						pw.destroy();break
			if transferMode == "cut":
				clipBoard = [] ; transferMode = "" ; reloadFiles()
			pw.destroy()
			return 'break'
	except Exception as e:
		if clipBoard == None:
			pass
		else:
			messagebox.showerror("Error!", "Error: " + str(e));return 'break'

def toggle_fullscreen(event=None):
	global state;state = not state;root.attributes("-fullscreen",state)
def sysdir():
	global linux
	print("Loaded sysdir() function")
	errdir = curPathText.get()
	print(errdir)
	if linux == True:
		os.chdir("/");curPathText.set("/");pll.set("/")
		reloadFiles()
	elif errdir == '' or errdir =="System Directory":
		try:
			root.title("System Directory - File Manager");ChangeText("System Directory");curPathText.set("System Directory")
			dc = win32api.GetLogicalDriveStrings();drives=dc.split('\000')[:-1]
			fileListBox.delete(*fileListBox.get_children());count = 0
			for d in drives:
				fileListBox.insert("","end",iid=d ,values = (d, "" , "Drive", "")) ; count += 1
			if count == 1 or 0:
				filecount.configure(text=str(count) + " item")
			else:
				filecount.configure(text=str(count) + " items")
			upbtn.configure(state=DISABLED)
		except:
			messagebox.showerror("Error", "Cannot collect the file list.")
	else:
		pass	

def select(index):
	try:
		fileListBox.selection_set(index)
	except:
		pass

def reloadFiles():
	global transferMode,items,search,stoprefresh
	if search == True:
		return 'break'
	selection = fileListBox.selection() ; fileListBox.delete(*fileListBox.get_children())
	try:
		flist = os.listdir(curPathText.get()) ; added = 0
		for ind, item in enumerate(flist):
			if function.file_size(item) is not None:
				name, extension = os.path.splitext(item)
				fileListBox.insert("","end",iid= item ,values = ("📄 " + item, time.ctime(os.path.getmtime(item)) , extension + " File" , function.file_size(item)))
			else:
				fileListBox.insert("","end",iid= item ,values = ("📁 " + item, time.ctime(os.path.getmtime(item)), "Folder" ,""))
			added += 1
			items +=1
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
		dirname = pl.split(splash)[-1]
		if dirname == "":
			dirname = pl
		select(selection);root.title(dirname + "- File Manager")
		if stoprefresh==True:
			pass
		else:
			ChangeText(pl)
	except (FileNotFoundError, UnboundLocalError, PermissionError):
		sysdir()

def openfunc():
	try:
		print(".")
		selection = fileListBox.selection() ; FName = fileListBox.focus()
		oldpath = os.getcwd() ; curPathText.set(oldpath) ; ChangeText(oldpath)
		if ":" in FName:
			curPathText.set(FName) ; os.chdir(FName)
			ChangeText(FName) ; reloadFiles()
			bck.append(oldpath)
		else:
			for f in selection:
				multiplefilePath = curPathText.get() + splash + str(f)
				if linux != True:
					os.startfile(multiplefilePath)
				else:
					opener = "open" if sys.platform == "darwin" else "xdg-open"
					subprocess.call([opener, multiplefilePath])
		upbtn.configure(state=DISABLED) if curPathText.get()=="System Directory" else upbtn.configure(state=NORMAL)
	except Exception as e:
		print(e)
		if e.errno == errno.ENOENT: 
			messagebox.showerror("An error occurred.", "Invaild file or directory name. Check the spelling and try again.")
		elif e.errno in [errno.EPERM, errno.EACCES]: 
			messagebox.showerror("An error occurred.", "You have no permission to access the path.")
		else:
			print(e)

def opensystem(event):
	global curPathText,curdata,stoprefresh,splash
	FName = fileListBox.focus() ; s = fileListBox.selection();lastdir = os.getcwd()
	try:
		i = fileListBox.identify_row(event.y)
		if i in s:
			try:

				FPath = curPathText.get() + splash + FName
				if ":" in FName:
					openfunc()
				elif function.file_size(FPath) == None:
					curdata = [];curPathText.set(FPath);ChangeText(FPath);os.chdir(FPath)
					reloadFiles();bck.append(lastdir)
				else:
					openfunc()
				print(function.file_size(FPath))
			except Exception as e:
				if linux != True:
					if e.errno == errno.ENOENT: 
						reloadFiles()
					elif e.errno in [errno.EPERM, errno.EACCES]: 
						messagebox.showerror("An error occurred.", "You have no permission to access.");stoprefresh=2
						os.chdir(lastdir);curPathText.set(lastdir);pll.set(lastdir);reloadFiles()
					else:
						print(e)
				else:
					messagebox.showerror("Error!", "Error: "+e)
		else:
			select("")
		upbtn.configure(state=DISABLED) if curPathText.get()=="System Directory" else upbtn.configure(state=NORMAL)
		stoprefresh=False
	except:
		openfunc()
	
def go(event):
	global linux,splash
	try:
		lastdir = os.getcwd()
		if "System Directory" == pll.get():
			sysdir()
		elif "" == pll.get():
			ChangeText(lastdir) ; curPathText.set(lastdir)
		elif splash not in pll.get():
				dir = pll.get() + splash ; curPathText.set(dir) ; os.chdir(dir) ; ChangeText(dir) ; reloadFiles()
				bck.append(os.getcwd())
		elif "maindir" == pll.get():
			sysdir()
		elif "." in pll.get():
			os.startfile(pll.get()) ; ChangeText(lastdir)
		else:
			curPathText.set(pll.get()) ; os.chdir(pll.get()) ; ChangeText(pll.get()) ; reloadFiles()
			if bck[-1] == os.getcwd():
				pass
			else:
				bck.append(os.getcwd())
		upbtn.configure(state=DISABLED) if curPathText.get()=="System Directory" else upbtn.configure(state=NORMAL)
	except Exception as error:
		if error.errno == errno.ENOENT: 
			messagebox.showerror("An error occurred.", "File Manager can't find '" + pll.get() + "'. Check the spelling and try again.")
		elif error.errno in [errno.EPERM, errno.EACCES]: 
			messagebox.showerror("An error occurred.", "You have no permission to access this directory.")
			curPathText.set(lastdir);pll.set(lastdir);os.chdir(lastdir)
		elif error.args[0] != 123:
			messagebox.showerror("An error occurred.", "No path named: '" + pll.get() + "'. Check the spelling and try again.")
		else:
			print(error)
		
def showfileinfo():
	try:
		appname = fileListBox.selection()
		tail_path = os.path.split(pll.get());backonedir=False;skipcurappdir=False
		if appname == ():
			appname = (tail_path[1], )
			if appname == ('',):
				appname = (os.getcwd(), );skipcurappdir=True
			else:
				backonedir = True;os.chdir("..");curPathText.set(os.getcwd())
		window = Toplevel(root);window.geometry("300x250");window.resizable(0,0)
		if linux != True:
			window.wm_attributes('-toolwindow', 'True')
		apptext = Label(window, text="...\n") ; typetext = Label(window, text="\nType of file: ...") ; sizetext = Label(window, text="Size: Calculating...")
		apptext.pack(side=TOP) ; typetext.pack(side=TOP) ; sizetext.pack(side=TOP)
		separator = Label (window, text=" ——————————————\n").pack(side=TOP)
		item = 0
		for fn in appname:
			if skipcurappdir==True:
				break
			else:
				item +=1
				name, extension = os.path.splitext(fn) ; curAppdir = curPathText.get() + splash + fn
		if item >= 2:
			window.destroy() if curPathText.get() =="System Directory" else 0
			window.title(str(item) + " files selected");apptext.configure(text=str(item)+" files selected") ; sizetext.configure(text="") ; typetext.configure(text="Type: Multiple types")
			return 'break'
		else:
			window.title(fn)
			try:
				if item >=2:
					pass
				else:
					ctime = Label(window, text="Created: "+time.ctime(os.path.getctime(fn)));mtime = Label(window, text="Modified: "+time.ctime(os.path.getmtime(fn))); atime = Label(window, text="Accessed: "+time.ctime(os.path.getatime(fn)))
					ctime.pack(side=TOP) ; mtime.pack(side=TOP) ; atime.pack(side=TOP)
			except:
				return 'break'
			try:
				try:
					apptext.configure(text=fn + "\n")
					if "." not in fn:
						raise TypeError
					size = function.file_size(curAppdir);sizetext.configure(text="Size: " + str(size));typetext.configure(text="Type of file: '" + extension + "'")
				except Exception as e:
					if curPathText.get() == "System Directory":
						raise OSError("")
					elif "\\" in fn:
						raise OSError
					else:
						typetext.configure(text="Type of file: Folder")
						size = function.get_folder_size(curAppdir);sizetext.configure(text="Size: " + size)
			except (OSError, PermissionError):
				if curPathText.get() == "System Directory" or "\\" in fn:
					try:
						total, used, free = shutil.disk_usage(fn)
						sizetext.configure(text="Total: %d GB" % (total // (2**30)) + "\nUsed: %d GB" % (used // (2**30)) + "\nFree: %d GB" % (free // (2**30)))
						typetext.configure(text="Type: Device (or driver)")
					except:
						sizetext.configure(text="Cannot detect the size");typetext.configure(text="")
						
				else:
					sizetext.configure(text="Cannot detect the size");typetext.configure(text="")
		try:
			if backonedir==True:
				os.chdir(str(tail_path[1]));curPathText.set(os.getcwd())
		except Exception as e:
			print(e)
	except Exception as e:
		print(e)
		window.destroy()	
		return'break'

def back():
	global bck,frwd
	try:
		frwd.append(bck[-1]);bck = bck[:-1]
	except:
		pass
	try:
		if str(bck[-1]) == "System Directory":
			curPathText.set("System Directory"); pll.set("System Directory"); sysdir();upbtn.configure(state=DISABLED)
		else:
			try:
				os.chdir(str(bck[-1]));ChangeText(str(bck[-1]));curPathText.set(str(bck[-1]));reloadFiles();upbtn.configure(state=NORMAL)
			except:
				pass
	except:
		pass
def forward():
	global bck,frwd
	try:
		bck.append(frwd[-1]);frwd = frwd[:-1]
	except:
		pass
	try:
		if str(frwd[-1]) == "System Directory":
			curPathText.set("System Directory"); pll.set("System Directory"); sysdir();upbtn.configure(state=DISABLED)
		else:
			try:
				os.chdir(str(frwd[-1]));ChangeText(str(frwd[-1]));curPathText.set(str(frwd[-1]));reloadFiles();upbtn.configure(state=NORMAL)
			except:
				pass
	except:
		pass
	
def searchfunc(event):
	global curdata,search
	search=True
	if curdata == []:
		curdata = fileListBox.get_children()
	else:
		pass

	value = sv.get();fileListBox.delete(*fileListBox.get_children())
	
	if value == '':
		search=False;reloadFiles();curdata = []
	if value == "Search...":
		pass
	else:
		filecount.configure(text="Search") ; data = [] ; root.title("Search Results");pll.set("Search Results")
		for item in curdata:
			if value in item.lower():
				data.append(item)
			else:
				pass
		for item in data:
			try:
				if curPathText.get() == "System Directory":
					fileListBox.insert("","end",iid=item ,values = ("🖴 " + item, "" , "Drive", ""))
				elif function.file_size(item) is not None:
					name, extension = os.path.splitext(item)
					fileListBox.insert("","end",iid= item ,values = ("📄 " + item, "" , extension + " File" , function.file_size(item)))
				else:
					fileListBox.insert("","end",iid= item ,values = ("📁 " + item, time.ctime(os.path.getmtime(item)), "Directory" ,""))
			except:
				pass

def click(*args):
	if sv.get() != 'Search...':
		pass
	else:
		search.delete(0, 'end')
  
def leave(*args):
	if sv.get() != "":
		return'break'
	search.delete(0, 'end');search.insert(0, 'Search...');root.focus()
def stopreload(*args):
	global stoprefresh
	stoprefresh=True
def reload(*args):
	global stoprefresh
	stoprefresh=False

def refresh():
	if items > 1000 or search==True:
		pass 
	elif stoprefresh==2:
		pass
	else:
		reloadFiles()
	root.after(3000, refresh)

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

root.after(3000,refresh)
file_mgr.title("File Manager")
file_mgr.geometry("800x500")
file_mgr.minsize(700, 400)

try:
	root.iconbitmap(default=ICON_PATH)
except:
	pass

root.bind("<F11>", toggle_fullscreen)

frame1=Frame(root);frame1.pack(side=TOP,fill=X)

toolbar=ttk.Frame(frame1);toolbar.pack(side=TOP,fill=X)
backbtn = ttk.Button(frame1, text="←",command=back,width=4)
backntip = function.CreateToolTip(backbtn, "Back")
backbtn.pack(side=LEFT,padx=1)
frwdbtn = ttk.Button(frame1, text="→", command=forward,width=4)
frwdbtntip = function.CreateToolTip(frwdbtn, "Forward")
frwdbtn.pack(side=LEFT)
upbtn = ttk.Button(frame1, text="↑", command=upward, width=2)
upbtntip = function.CreateToolTip(upbtn, "Up")
upbtn.pack(side=LEFT,padx=2	)
sv = StringVar()
search = ttk.Entry(frame1,width=25, textvariable = sv)
search.pack(side=RIGHT, padx=2)
search.insert(0, 'Search...')
search.bind('<FocusOut>', leave);search.bind('<KeyRelease>', searchfunc);search.bind("<Button-1>", click)
refreshbtn = ttk.Button(frame1, text="↻", command=reloadFiles, width=4)
refreshbtntip = function.CreateToolTip(refreshbtn, "Refresh")
refreshbtn.pack(side=RIGHT,padx=1)
gobtn = ttk.Button(frame1, text="↩", command=lambda:go(root), width=4)
gobtntp = function.CreateToolTip(gobtn, "Go to the path you typed in the adrress bar")
gobtn.pack(side=RIGHT, padx=4)

path = ttk.Entry(frame1,  textvariable = pll)
path.pack(side=LEFT, fill=BOTH, expand=1)

path.bind("<Return>", go);path.bind('<KeyRelease>', stopreload);path.bind('<FocusOut>', reload)

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
rightclick.add_command(label ="Cut", command=lambda:cut(root))
rightclick.add_command(label ="Copy", command=lambda:copy(root))
rightclick.add_command(label ="Rename", command=lambda:renameSelectedFile(root))
rightclick.add_command(label="Delete", command=lambda:deleteSelectedFile(root))
rightclick.add_separator()
rightclick.add_command(label="Info", command=lambda:Thread(target=showfileinfo).start())

rc2 = Menu(root, tearoff= 0) #right click when the selection is nothing
rc2new = Menu(root, tearoff=0) ; rc2new.add_command(label="New folder", command=lambda:newFolder(root)), rc2new.add_command(label="New file", command=lambda:newFile(root))
rc2.add_command(label ="Paste", command=lambda:Thread(target=paste, args=str(root)).start()) ; rc2.add_separator() ; rc2.add_cascade(label="New", menu=rc2new)
rc2.add_command(label ="Refresh", command=reloadFiles); rc2.add_command(label="Info", command=showfileinfo)

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
	except:
		pass

def do_popup(event):
	RClickChecker() ; checkselect(event)
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

def RClickChecker():
	count = 0
	for c in fileListBox.selection():
		count +=1
	rc2.entryconfig("Paste", state="disabled") if clipBoard == [] or search==True else rc2.entryconfig("Paste", state="normal")
	rightclick.entryconfig("Rename", state="disabled") if count >=2 else rightclick.entryconfig("Rename", state="normal")
	rc2.entryconfig("Info", state="disabled") if search==True or curPathText.get() == "System Directory" else rc2.entryconfig("Info", state="normal")

fileListBox.bind("<Button-3>", do_popup) ; fileListBox.bind('<<ListboxSelect>>') ; fileListBox.bind("<Double-Button-1>", opensystem)
fileListBox.bind("<Delete>", deleteSelectedFile) ; fileListBox.bind("<Control-c>",copy) ; fileListBox.bind("<Control-x>", cut)
root.bind("<F2>", renameSelectedFile);root.bind("<Control-v>", paste); fileListBox.bind('<Button-2>',lambda x:select(""))
fileListBox.bind("<Control-a>",lambda x:select(fileListBox.get_children()))

reloadFiles()

m.add(fileListBox)

if(__name__ == "__main__"):
	root.mainloop()
