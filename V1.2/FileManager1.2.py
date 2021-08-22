from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
import shutil         
import os
import tkinter
from django.utils.text import get_valid_filename
import django
import os, re




    
root = Tk()

clipBoard = None

fileListBox = None
textArea = None

curPathText = StringVar()
curPathText.set(os.getcwd())

	
#for clearing the window
def all_children (window) :
	_list = window.winfo_children()
	for item in _list:
		if item.winfo_children():
			_list.extend(item.winfo_children())
	return _list

def clear_root():
	widgets = all_children(root)
	for widget in widgets:
		widget.pack_forget() #clear all widgets from window

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
	except django.core.exceptions.SuspiciousFileOperation:
		os.makedirs("New Folder")
def renameSelectedFile(parent):
	try:
		fileName = curPathText.get() + "\\" + fileListBox.get(fileListBox.curselection())
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
	except django.core.exceptions.SuspiciousFileOperation:
		pass
def deleteSelectedFile():
	try:
		fileName = fileListBox.get(fileListBox.curselection())
		confirmDelete = messagebox.askokcancel("","Confirm to delete " + fileName + "?")
		if(confirmDelete):
			os.remove(curPathText.get() + "\\" + fileName)
			reloadFiles(0)
	except (TclError, PermissionError) as e:
		messagebox.showerror("Error", "Error to delete that file because:")
		messagebox.showerror("Error Reason", e)

def enterFolder():
	global curPathText
	try:
		folderName = fileListBox.get(fileListBox.curselection())
		newPath = curPathText.get() + "\\" + folderName
		if(os.path.isdir(newPath)):
			curPathText.set(newPath)
			os.chdir(newPath)
			reloadFiles()
		else:
			messagebox.showinfo("Error", folderName + " is not a folder")
	except:
		messagebox.showinfo("Error", "Unable to enter folder")

def upward():
	curPathText.set(('\\').join(curPathText.get().split("\\")[:-1]))
	os.chdir("..")
	reloadFiles()

def copy():
	global clipBoard
	global transferMode
	clipBoard = curPathText.get() + "\\" + fileListBox.get(fileListBox.curselection())
	transferMode = "copy"
	print("Copied", clipBoard)

def cut():
	global clipBoard
	global transferMode
	clipBoard = curPathText.get() + "\\" + fileListBox.get(fileListBox.curselection())
	transferMode = "cut"
	print("Cut", clipBoard)

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
	reloadFiles()

def about():
	messagebox.showinfo("About", "📁 File Explorer V1.2\n Made by LNogDEV..")

#load the menu bar
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

	navMenu.add_command(label="Reload", command=reloadFiles)
	navMenu.add_command(label="Enter", command=enterFolder)
	navMenu.add_command(label="Up", command=upward)

	helpMenu.add_command(label="About", command=about)

	menuBar.add_cascade(label="File", menu=fileMenu)
	menuBar.add_cascade(label="Nav", menu=navMenu)
	menuBar.add_cascade(label="Help", menu=helpMenu)
	root.config(menu=menuBar)



#populates file listbox with files in directory
def reloadFiles(fileToSelect = None):
	fileListBox.delete(0,END)
	try:
		flist = os.listdir(curPathText.get())
		selectionInd = 0
		added = 0
		for ind, item in enumerate(flist):
			if(not (fileToSelect is None)):
				if(fileToSelect == item):
					selectionInd = added
			fileListBox.insert(END, item)
			added += 1
		fileListBox.selection_set(selectionInd)
		pl = os.getcwd()
		ChangeText(pl)
	except (FileNotFoundError, UnboundLocalError):	
		try:
			ChangeText("System Directory")
			driver = re.findall(r"[A-Z]+:.*$",os.popen("mountvol /").read(),re.MULTILINE)

			for f in driver:
				fileListBox.insert(END, f)
		except:
			messagebox.showerror("Error", "Cannot collect the file list.")
def opensystem(event):
	global curPathText
	try:
		folderName = fileListBox.get(fileListBox.curselection())
		newPath = curPathText.get() + "\\" + folderName
		if ":" in folderName:
			curPathText.set(folderName)
			os.chdir(folderName)
			ChangeText(folderName)
			reloadFiles()
		if(os.path.isdir(newPath)):
			curPathText.set(newPath)
			os.chdir(newPath)
			ChangeText(newPath)
			reloadFiles()
		else:
			try:
				os.startfile(newPath)
			except OSError:
				pass
				reloadFiles()
	except:
		messagebox.showinfo("Error", "Unable to enter folder or run file")

def go(event):
	try:
		lastdir = os.getcwd()
		curPathText.set(pll.get())
		os.chdir(pll.get())
		ChangeText(pll.get())
		reloadFiles()
	except (OSError, TypeError):
		messagebox.showerror("an error occurred.", "Cannot enter to the specific directory. Please check again.")
		curPathText.set(lastdir)
		ChangeText(lastdir)
		os.chdir(lastdir)

#main file explorer window
clear_root()
	
frame1=Frame(root)
frame1.pack(side=TOP,fill=X)

file_mgr = root
file_mgr.title("Files Manager")
file_mgr.geometry("800x500")
	
toolbar=Frame(frame1)
toolbar.pack(side=TOP,fill=X)
upbtn = tkinter.Button(frame1, text="↑ Up", command=upward)
upbtn.pack(side=LEFT,padx=1)
refreshbtn = tkinter.Button(frame1, text="↻ Refresh", command=reloadFiles)
refreshbtn.pack(side=LEFT,padx=1)
newfolderbtn = tkinter.Button(frame1, text="New 📁", command=lambda: newFolder(root))
newfolderbtn.pack(side=RIGHT, padx=1)
newfilebtn = tkinter.Button(frame1, text="+File", command=lambda: newFile(root))
newfilebtn.pack(side=RIGHT, padx=1)
delfilebtn = tkinter.Button(frame1, text="✖ Delete", command=deleteSelectedFile)
delfilebtn.pack(side=RIGHT, padx=1)
copybtn = tkinter.Button(frame1, text="Copy", command=copy)
copybtn.pack(side=RIGHT, padx=1)
cutbtn = tkinter.Button(frame1, text="✂Cut", command=cut)
cutbtn.pack(side=RIGHT, padx=1)
pastebtn = tkinter.Button(frame1, text="Paste", command=paste)
pastebtn.pack(side=RIGHT, padx=1)
gobtn = tkinter.Button(frame1, text="↩Go", command=lambda:go(root))
gobtn.pack(side=RIGHT, padx=4)
def ChangeText(text):
	pll.set(text)

pll = tkinter.StringVar()

path = tkinter.Entry(frame1,  textvariable = pll)
path.pack(side=LEFT, fill=BOTH, expand=1)

path.bind("<Return>", go)

m = PanedWindow(file_mgr,orient="horizontal")
m.pack(fill=BOTH ,expand=1)

fileListBox = Listbox(m, name='fileListBox')
fileListBox.bind('<<ListboxSelect>>')
fileListBox.bind("<Double-Button-1>", opensystem)	
scrollbar = Scrollbar(m)
scrollbar.pack(side = RIGHT, fill = BOTH)

for values in range(100):
	fileListBox.insert(END, values)

fileListBox.config(yscrollcommand = scrollbar.set)
scrollbar.config(command = fileListBox.yview)

rightclick = Menu(root, tearoff = 0)
rightclick.add_command(label="Open", command=lambda:opensystem(root))
rightclick.add_command(label ="Cut", command=cut)
rightclick.add_command(label ="Copy", command=copy)
rightclick.add_command(label ="Paste", command=paste)
rightclick.add_command(label ="Refresh", command=reloadFiles)
rightclick.add_separator()
rightclick.add_command(label ="Rename", command=lambda:renameSelectedFile(root))
	
def do_popup(event):
	try:
		rightclick.tk_popup(event.x_root, event.y_root)
	finally:
		rightclick.grab_release()

fileListBox.bind("<Button-3>", do_popup)

reloadFiles() #populate

m.add(fileListBox)

menu_bar(file_mgr)


if(__name__ == "__main__"):
	root.mainloop()
