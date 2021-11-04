import serial
import serial.tools.list_ports
import os
import tkinter as tk
from tkinter import ttk
from tkinter import*
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

window = Tk()
window.geometry("500x200")
window.title('Star Adventurer GOTO Interface')
window.configure(bg='black')

serialmonitor = Tk()
serialmonitor.geometry("550x200")
serialmonitor.title('Serial Monitor')

#Empty string to initialize the variable which stores the COM port number
SerialConnection = ""

#Empty string to initialize the variable which stores the .txt object catalog file
filename = filedialog.askopenfilename(title = 'Please Select Object Catalog File',filetypes = (("Text Files","*.txt"),))
InputFile = open(filename, 'r')

ConnectedSerialDevices = []
RawFileContents = []
Targets = []
SourceCoordinates = []
DestinationCoordinates = []

SourceEnum = StringVar(window)
DestinationEnum = StringVar(window)
COMPortVar = IntVar()

comlist = serial.tools.list_ports.comports()
for element in comlist:
    ConnectedSerialDevices.append(element.device)

def CreateSerial():
    global SerialConnection
    if SerialConnection == "":
        try:
            SerialConnection = serial.Serial(port=ConnectedSerialDevices[0], baudrate=115200, timeout=1)
            COMPortVar.set(1)
            SerialResponse.insert('end', 'SERIAL CONNECTION CREATED: ' + SerialConnection.name + ', baudrate:115200, timeout=1\n')
        except serial.SerialException:
            try:
                raise messagebox.showwarning(message='Invalid input! could not establish serial connection with the given information, please try again.')
            except TypeError:
                pass
    else:
        SerialConnection = ""
        COMPortVar.set(0)

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
    RAString.delete('1.0', 'end')
    DEString.delete('1.0', 'end')
    sourcecoordinates = SourceCoordinates[Targets.index(SourceEnum.get())].split(',')
    destinationcoordinates = DestinationCoordinates[Targets.index(DestinationEnum.get())].split(',')
    coordinatedifference = []
    for i in range(len(sourcecoordinates)):
        x = int(sourcecoordinates[i]) - int(destinationcoordinates[i])
        coordinatedifference.append(x)
    RAdegrees = round((((coordinatedifference[0] * 60) + coordinatedifference[1] + (coordinatedifference[2] / 60)) / 60) * 15, 2)
    DEdegrees = round(coordinatedifference[3] + (coordinatedifference[4] / 60) + (coordinatedifference[5] / 3600), 2)
    CoordDiffLabel['text'] = 'Coordinate Difference RA Degrees/DE Degrees: [' + str(RAdegrees) + ',' + str(DEdegrees) + ']'
    RAString.insert('end', '1,' + str(GetDirection(RAdegrees)) + ',20,' + str(abs(RAdegrees)) + ',0')
    DEString.insert('end', '0,' + str(GetDirection(DEdegrees)) + ',20,' + str(abs(DEdegrees)) + ',0')

def GetDirection(number):
    if number < 0:
        return 0
    else:
        return 1

def MoveRA():
    string = RAString.get('1.0', 'end')
    try:
        SerialError()
    except TypeError:
        pass
    else:
        RAString.delete('1.0', 'end')
        SerialConnection.write(bytes(string, 'utf-8'))
        SerialConnection.flush()
        response = SerialConnection.readlines()
        for i in response:
            SerialResponse.insert('end', i)
        SerialResponse.see('end')

def MoveDE():
    string = DEString.get('1.0', 'end')
    try:
        SerialError()
    except TypeError:
        pass
    else:
        DEString.delete('1.0', 'end')
        SerialConnection.write(bytes(string, 'utf-8'))
        SerialConnection.flush()
        response = SerialConnection.readlines()
        for i in response:
            SerialResponse.insert('end', i)
        SerialResponse.see('end')

ParseCatalogFile()

MasterFrame1 = Frame(window, height=0, width=0, bg='black')
MasterFrame1.pack(padx=1, pady=1, side=TOP)

MasterFrame2 = Frame(window, height=0, width=0, bg='black')
MasterFrame2.pack(padx=1, pady=1, side=TOP)

MasterFrame3 = Frame(window, height=0, width=0, bg='black')
MasterFrame3.pack(padx=1, pady=1, side=TOP)

MasterFrame4 = Frame(window, height=0, width=0, bg='black')
MasterFrame4.pack(padx=1, pady=1, side=TOP)

MasterFrame5 = Frame(window, height=0, width=0, bg='black')
MasterFrame5.pack(padx=1, pady=1, side=TOP)

MasterFrame6 = Frame(window, height=0, width=0, bg='black')
MasterFrame6.pack(padx=1, pady=10, side=BOTTOM)

SourceFrame = Frame(MasterFrame1, height=0, width=0, bg='black')
SourceFrame.pack(padx=1, pady=1, side=LEFT)

DestinationFrame = Frame(MasterFrame2, height=0, width=0, bg='black')
DestinationFrame.pack(padx=1, pady=1, side=LEFT)

SourceDropdown = ttk.OptionMenu(SourceFrame, SourceEnum, Targets[0], *Targets, command=DisplaySourceCoordinates)
SourceDropdown.pack(padx=1, pady=1, side=RIGHT)

DestinationDropdown = ttk.OptionMenu(DestinationFrame, DestinationEnum, Targets[0], *Targets, command=DisplayDestinationCoordinates)
DestinationDropdown.pack(padx=1, pady=1, side=RIGHT)

SourceObject = Label(SourceFrame, text='Source Target: ', bg='black', fg='white')
SourceObject.pack(padx=1, pady=1, side=LEFT)

DestinationObject = Label(DestinationFrame, text='Destination Target: ', bg='black', fg='white')
DestinationObject.pack(padx=1, pady=1, side=LEFT)

SourceCoordLabel = Label(MasterFrame1, text='Source Coordinates RA/DE: ', bg='black', fg='white')
SourceCoordLabel.pack(padx=1, pady=1, side=RIGHT)

DestinationCoordLabel = Label(MasterFrame2, text='Destination Coordinates RA/DE: ', bg='black', fg='white')
DestinationCoordLabel.pack(padx=1, pady=1, side=RIGHT)

CoordDiffLabel = Label(MasterFrame3, text='Coordinate Difference RA/DE: ', bg='white')
CoordDiffLabel.pack(padx=1, pady=1, side=TOP)

RAStringLabel = Label(MasterFrame4, text='Right Ascension Movement String: ', bg='black', fg='white')
RAStringLabel.pack(padx=1, pady=1, side=LEFT)

RAString = Text(MasterFrame4, width=15, height=1, bd=0, fg='#fb00ff')
RAString.pack(padx=1, pady=1, side=RIGHT)

DEStringLabel = Label(MasterFrame5, text='Declination Movement String: ', bg='black', fg='white')
DEStringLabel.pack(padx=1, pady=1, side=LEFT)

DEString = Text(MasterFrame5, width=15, height=1, bd=0, fg='#fb00ff')
DEString.pack(padx=1, pady=1, side=RIGHT)

MoveRAButton = Button(MasterFrame6, text='GOTO RA Axis', command=MoveRA)
MoveRAButton.pack(padx=80, pady=1, side=LEFT)

MoveDEButton = Button(MasterFrame6, text='GOTO DE Axis', command=MoveDE)
MoveDEButton.pack(padx=80, pady=1, side=RIGHT)

SerialResponse = Text(serialmonitor, height=int(serialmonitor.winfo_screenwidth()), width=int(serialmonitor.winfo_screenwidth()))
SerialResponse.pack(padx=1, pady=1, side=TOP)

topmenu = Menu()
file = Menu(window, tearoff=0)
topmenu.add_cascade(label='File', menu=file, state='active')
serialmenu = Menu(file, tearoff=0)
file.add_cascade(label='COM Device', menu=serialmenu, state='active')
serialmenu.add_checkbutton(label=ConnectedSerialDevices[0], variable=COMPortVar, onvalue=1, offvalue=0, command=CreateSerial)
file.add_separator()
file.add_command(label='About', command=About)
file.add_separator()
file.add_command(label='Exit', command=window.destroy)

window.configure(menu=topmenu)

window.mainloop()