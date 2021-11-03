import serial
import os
import tkinter as tk
from tkinter import ttk
from tkinter import*
from tkinter import messagebox
from tkinter import simpledialog

window = Tk()
window.geometry("500x200")
window.title('Star Adventurer GOTO Interface')

#Empty string to initialize the variable which stores the COM port number
SerialConnection = ""
#Empty string to initialize the variable which stores the .txt object catalog file
InputFile = open('database.txt', 'r')

RawFileContents = []
Targets = []
SourceCoordinates = []
DestinationCoordinates = []

SourceEnum = StringVar(window)
DestinationEnum = StringVar(window)

def CreateSerial():
    x = simpledialog.askstring('input string', 'Enter the COM port shown in parentheses next to the detected Star Adventurer GOTO Controller listed under "Ports (COM & LPT)" dropdown within the windows device manager.')
    try:
        SerialConnection = serial.Serial(port=x, baudrate=9600, timeout=1)
    except serial.SerialException:
        try:
            raise messagebox.showwarning(message='Invalid input! could not establish serial connection with the given information, please try again.')
        except TypeError:
            pass

def SerialError():
    global SerialConnection
    if SerialConnection == "":
        raise messagebox.showwarning(message='Please configure a serial connection first from the "COM Device" dropdown in the upper file menu!')

def About():  # About software info section
    messagebox.showinfo(title='About', message='Designed by Fabian Butkovich, super engineer extraordinaire')

def ParseCatalogFile():
    global RawFileContents, Targets, SourceCoordinates, DestinationCoordinates
    RawFileContents = InputFile.readlines()
    temp = []
    for i in RawFileContents:
        Targets.append(i.split(':')[0])
        SourceCoordinates.append(i.split(':')[1])
    for n in SourceCoordinates:
        temp.append(n.replace('\n', ''))
    SourceCoordinates = temp
    DestinationCoordinates = SourceCoordinates
    InputFile.close()

def DisplaySourceCoordinates(choice):
    choice = SourceEnum.get()
    SourceCoordLabel['text'] = 'Source Coordinates RA/DE: ' + SourceCoordinates[Targets.index(choice)]

def DisplayDestinationCoordinates(choice):
    choice = DestinationEnum.get()
    DestinationCoordLabel['text'] = 'Destination Coordinates RA/DE: ' + DestinationCoordinates[Targets.index(choice)]
    CalculateCoordinateDifference()

def CalculateCoordinateDifference():
    sourcecoordinates = SourceCoordinates[Targets.index(SourceEnum.get())].split(',')
    destinationcoordinates = DestinationCoordinates[Targets.index(DestinationEnum.get())].split(',')
    coordinatedifference = []
    for i in range(len(sourcecoordinates)):
        x = int(sourcecoordinates[i]) - int(destinationcoordinates[i])
        coordinatedifference.append(x)
    RAdegrees = round((((coordinatedifference[0] * 60) + coordinatedifference[1] + (coordinatedifference[2] / 60)) / 60) * 15, 2)
    DEdegrees = round(coordinatedifference[3] + (coordinatedifference[4] / 60) + (coordinatedifference[5] / 3600), 2)
    CoordDiffLabel['text'] = 'Coordinate Difference RA Degrees/DE Degrees: ' + '[' + str(RAdegrees) + ',' + str(DEdegrees) + ']'

ParseCatalogFile()

MasterFrame1 = Frame(window, height=0, width=0)
MasterFrame1.pack(padx=1, pady=1, side=TOP)

MasterFrame2 = Frame(window, height=0, width=0)
MasterFrame2.pack(padx=1, pady=1, side=TOP)

MasterFrame3 = Frame(window, height=0, width=0)
MasterFrame3.pack(padx=1, pady=1, side=TOP)

SourceFrame = Frame(MasterFrame1, height=0, width=0)
SourceFrame.pack(padx=1, pady=1, side=LEFT)

DestinationFrame = Frame(MasterFrame2, height=0, width=0)
DestinationFrame.pack(padx=1, pady=1, side=LEFT)

SourceDropdown = ttk.OptionMenu(SourceFrame, SourceEnum, Targets[0], *Targets, command=DisplaySourceCoordinates)
SourceDropdown.pack(padx=1, pady=1, side=RIGHT)

DestinationDropdown = ttk.OptionMenu(DestinationFrame, DestinationEnum, Targets[0], *Targets, command=DisplayDestinationCoordinates)
DestinationDropdown.pack(padx=1, pady=1, side=RIGHT)

SourceObject = Label(SourceFrame, text='Source Target: ')
SourceObject.pack(padx=1, pady=1, side=LEFT)

DestinationObject = Label(DestinationFrame, text='Destination Target: ')
DestinationObject.pack(padx=1, pady=1, side=LEFT)

SourceCoordLabel = Label(MasterFrame1, text='Source Coordinates RA/DE: ')
SourceCoordLabel.pack(padx=1, pady=1, side=RIGHT)

DestinationCoordLabel = Label(MasterFrame2, text='Destination Coordinates RA/DE: ')
DestinationCoordLabel.pack(padx=1, pady=1, side=RIGHT)

CoordDiffLabel = Label(MasterFrame3, text='Coordinate Difference RA/DE: ', bg='white')
CoordDiffLabel.pack(padx=1, pady=1, side=TOP)

topmenu = Menu()
file = Menu(window, tearoff=0)
topmenu.add_cascade(label='File', menu=file, state='active')
serialmenu = Menu(file, tearoff=0)
file.add_cascade(label='COM Device', menu=serialmenu, state='active')
serialmenu.add_command(label='Establish Serial Connection', command=CreateSerial)
file.add_separator()
file.add_command(label='About', command=About)
file.add_separator()
file.add_command(label='Exit', command=window.destroy)

window.configure(menu=topmenu)

window.mainloop()