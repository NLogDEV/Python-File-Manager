from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
import shutil         
import os
import tkinter
from django.utils.text import get_valid_filename

    
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
		return	
	print("New file", name)
	f = open(name,"w+")
	f.write("")
	f.close()
	reloadFiles(name)

def newFolder(parent):
	name = get_valid_filename(simpledialog.askstring("Input", "Please enter the file name:",
                                parent=parent))
	if not os.path.exists(name):
		os.makedirs(name)

def renameSelectedFile(parent):
	fileName = curPathText.get() + "\\" + fileListBox.get(fileListBox.curselection())
	in_ = get_valid_filename(simpledialog.askstring("Input", "Please enter the new file name:", parent=parent))
	if(in_ is None):
		return
	newName = curPathText.get() + "\\" + in_
	os.rename(fileName, newName)
	reloadFiles(newName)

def saveSelectedFile():
	try:
		fileName = fileListBox.get(fileListBox.curselection())
		fullFileName = curPathText.get() + "\\" + fileName
		f = open(fullFileName,"w+")
		f.write(textArea.get("1.0",END))
		f.close()
		messagebox.showinfo("Information","Saved " + fileName + " successfully!")
	except:
		messagebox.showinfo("Information", "Make a new file before saving, or select existing file")

def deleteSelectedFile():
	try:
		fileName = fileListBox.get(fileListBox.curselection())
		confirmDelete = messagebox.askokcancel("","Confirm to delete " + fileName + "?")
		if(confirmDelete):
			os.remove(curPathText.get() + "\\" + fileName)
			reloadFiles(0)
	except TclError:
		messagebox.showerror("Error", "Error to run the delete command. Please select a file to continue.")

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
	messagebox.showinfo("About", "📁File Explorer V1.0\n Made by NLogDEV.")

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
	fileMenu.add_command(label="Save", command=saveSelectedFile)
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
	except FileNotFoundError:
		messagebox.showerror("Error", "Error collect the file list.")
	selectionInd = 0
	added = 0
	for ind, item in enumerate(flist):
		if(not (fileToSelect is None)):
			if(fileToSelect == item):
				selectionInd = added
		fileListBox.insert(END, item)
		added += 1
	fileListBox.selection_set(selectionInd)

def opensystem(event):
	global curPathText
	try:
		folderName = fileListBox.get(fileListBox.curselection())
		newPath = curPathText.get() + "\\" + folderName
		if(os.path.isdir(newPath)):
			curPathText.set(newPath)
			os.chdir(newPath)
			reloadFiles()
		else:
			try:
				os.startfile(newPath)
			except OSError:
				messagebox.showerror("Error", "Error to run the file or change the driectory to  '" + newPath + "'")
				reloadFiles()
	except:
		messagebox.showinfo("Error", "Unable to enter folder or run file")
	

#main file explorer window
def file_mgr():
	clear_root()
	
	global fileListBox #lists files
	global textArea #text editor for edits
	
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
	newfolderbtn.pack(side=LEFT, padx=1)
	newfilebtn = tkinter.Button(frame1, text="+File", command=lambda: newFile(root))
	newfilebtn.pack(side=LEFT, padx=1)
	delfilebtn = tkinter.Button(frame1, text="✖ Delete", command=deleteSelectedFile)
	delfilebtn.pack(side=LEFT, padx=1)
	copybtn = tkinter.Button(frame1, text="Copy", command=copy)
	copybtn.pack(side=LEFT, padx=1)
	cutbtn = tkinter.Button(frame1, text="✂Cut", command=cut)
	cutbtn.pack(side=LEFT, padx=1)
	pastebtn = tkinter.Button(frame1, text="Paste", command=paste)
	pastebtn.pack(side=LEFT, padx=1)

	m = PanedWindow(file_mgr,orient="horizontal")
	m.pack(fill=BOTH ,expand=1)
	
	fileListBox = Listbox(m, name='fileListBox')
	fileListBox.bind('<<ListboxSelect>>')
	fileListBox.bind("<Double-Button-1>", opensystem)	
	reloadFiles() #populate

	m.add(fileListBox)

	menu_bar(file_mgr)


if(__name__ == "__main__"):
	file_mgr()
	root.mainloop()
