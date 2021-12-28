import serial
import serial.tools.list_ports
import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import*
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog

#Create tkinter window for controls
window = Tk()
window.geometry("500x200")
window.title('Star Adventurer GOTO Interface')
window.configure(bg='black')

#Create tkinter window for serial monitor that reads response from Star Adventurer GOTO controller
serialmonitor = Tk()
serialmonitor.geometry("550x200")
serialmonitor.title('Serial Monitor')

#Empty string to initialize the variable which stores the COM port number
SerialConnection = ""

#Prompt user to select database catalog file to use
filename = filedialog.askopenfilename(title = 'Please Select Object Catalog File',filetypes = (("Text Files","*.txt"),))
#Open the .txt file for read only using the previously user provided file name and path
InputFile = open(filename, 'r')

#List of detected serial com ports that match the "Arduino" filtering case match
ConnectedSerialDevices = []
#List of raw contents read from .txt database file which stores object catalog
RawFileContents = []
#List of targets which are parsed from RawFileContents using ":" delimiter
Targets = []
SourceCoordinates = []
DestinationCoordinates = []

#Enum variables which are used to index several lists that are used by the entire application
SourceEnum = StringVar(window)
DestinationEnum = StringVar(window)

#Enum variable which is used to store which com port is selected
COMPortVar = IntVar()

#Use serial.tools method to retrieve list of available com port numbers and device names
comlist = serial.tools.list_ports.comports()

#Helper function for creating a serial connection if there isn't one established already
def CreateSerial():
    #Must create explicit reference to global serial connection variable or else function will create its own local variable
    global SerialConnection
    if SerialConnection == "":
        try:
            SerialConnection = serial.Serial(port=ConnectedSerialDevices[0], baudrate=9600, timeout=0, writeTimeout=0)
            SerialResponse.insert('end', 'SERIAL CONNECTION CREATED: ' + SerialConnection.name + ', baudrate:' + str(SerialConnection.baudrate) + ', timeout=' + str(SerialConnection.timeout) + ', writeTimeout=' + str(SerialConnection.writeTimeout) + '\n')
            SerialResponse.insert('end', '--------------------------------------------------------------\n')
        except serial.SerialException:
            try:
                raise messagebox.showwarning(message='Invalid input! could not establish serial connection with the given information, please try again.')
            except TypeError:
                pass
    else:
        SerialResponse.insert('end', 'SERIAL CONNECTION TERMINATED\n')
        SerialResponse.insert('end', '--------------------------------------------------------------\n')
        SerialConnection = ""

#Called every time a query is made to read the serial port to prevent runtime errors
def SerialError():
    #Must create explicit reference to global serial connection variable or else function will create its own local variable
    global SerialConnection
    if SerialConnection == "":
        raise messagebox.showwarning(message='Please configure a serial connection first from the "COM Device" dropdown in the upper file menu!')

def About():  # About software info section
    messagebox.showinfo(title='About', message='Designed by Fabian Butkovich, super engineer extraordinaire')

#Main function for parsing the object catalog .txt file and extracting object coordinates and names
def ParseCatalogFile():
    global RawFileContents, Targets, SourceCoordinates, DestinationCoordinates
    RawFileContents = InputFile.readlines()
    #Temporary list for storing every line after the ":" delimiter
    temp = []
    for i in RawFileContents:
        Targets.append(i.split(':')[0])
        SourceCoordinates.append(i.split(':')[1])
    #Use the .replace method to truncate the newline character at the end of every incoming readline
    for n in SourceCoordinates:
        temp.append(n.replace('\n', ''))
    #Copy contents of temp to DestinationCoordinates and SourceCoordinates lists
    SourceCoordinates = temp
    DestinationCoordinates = SourceCoordinates
    #Properly close .txt catalog file
    InputFile.close()

def DisplaySourceCoordinates(choice):
    #Get the value of the ingeter variable which is used to index which coordinates are displayed in the coordinates label for the source target
    choice = SourceEnum.get()
    #Set label text to string element from index retrived from choice
    SourceCoordLabel['text'] = 'Source Coordinates RA/DE: ' + SourceCoordinates[Targets.index(choice)]
    CalculateCoordinateDifference()

def DisplayDestinationCoordinates(choice):
    choice = DestinationEnum.get()
    DestinationCoordLabel['text'] = 'Destination Coordinates RA/DE: ' + DestinationCoordinates[Targets.index(choice)]
    CalculateCoordinateDifference()

#This function calculates the coordinate difference on both right ascension and declination axis' and creates a parameter string to be sent to controller
def CalculateCoordinateDifference():
    #Empty existing parameter strings from text widgets
    RAString.delete('1.0', 'end')
    DEString.delete('1.0', 'end')
    #Separate indexed coordinate string from source coordinates list using the .split method and ',' delimiter
    sourcecoordinates = SourceCoordinates[Targets.index(SourceEnum.get())].split(',')
    destinationcoordinates = DestinationCoordinates[Targets.index(DestinationEnum.get())].split(',')
    #Temporary list for storing computed coordinate differences between source and destination targets
    coordinatedifference = []
    #Calculate the differences between all RA coordinate numbers and all DE coordinate numbers (i.e. [23,33,4] - [2,3,1])
    for i in range(len(sourcecoordinates)):
        x = int(sourcecoordinates[i]) - int(destinationcoordinates[i])
        coordinatedifference.append(x)
    #Convert coordinate difference for RA axis into angular degrees using RA HH:MM:SS * 15
    RAdegrees = round((((coordinatedifference[0] * 60) + coordinatedifference[1] + (coordinatedifference[2] / 60)) / 60) * 15, 2)
    #Convert coordinate difference for DE axis into angular degrees using Deg + Arcmin/60 + Arcsec/60
    DEdegrees = round(coordinatedifference[3] + (coordinatedifference[4] / 60) + (coordinatedifference[5] / 3600), 2)
    CoordDiffLabel['text'] = 'Coordinate Difference RA Degrees/DE Degrees: [' + str(RAdegrees) + ',' + str(DEdegrees) + ']'
    RAString.insert('end', '0,' + str(GetDirectionRA(RAdegrees)) + ',10,' + str(abs(RAdegrees)) + ',1')
    DEString.insert('end', '1,' + str(GetDirectionDE(DEdegrees)) + ',10,' + str(abs(DEdegrees)) + ',1')

#Inverse direction control for RA axis
def GetDirectionRA(number):
    if number < 0:
        return 0
    else:
        return 1

def GetDirectionDE(number):
    if number < 0:
        return 1
    else:
        return 0

#Function which moves the right ascension axis by the necessary angular degrees to reach the destination target
def MoveRA():
    string = RAString.get('1.0', 'end')
    RAString.delete('1.0', 'end')
    #Pass the 5 element string parameter which is used to control the mount to the function which actually writes the serial data
    SerialWriteData(string)

#Function which moves the declination axis by the necessary angular degrees to reach the destination target
def MoveDE():
    string = DEString.get('1.0', 'end')
    DEString.delete('1.0', 'end')
    SerialWriteData(string)

#Receive parameter string to be sent to controller from caller functions above and write to serial port
def SerialWriteData(string):
    try:
        SerialError()
    except TypeError:
        pass
    else:
        SerialConnection.write(bytes(string, 'utf-8'))
        SerialConnection.flush()

#This function runs continously once a serial connection is established and repeatedly reads incoming serial
#data and populates the serial monitor text if there is anything new
def SerialReadResponse():
    if SerialConnection != "":
        try:
            SerialError()
        except TypeError:
            pass
        else:
            response = SerialConnection.readlines()
            for i in response:
                SerialResponse.insert('end', i)
    #This function calls itself repeatedly after being called initially and always checks for incoming serial
    #data to be printed out to the serial monitor, only IF there is an activer serial connection with the specified COM port, otherwise and error would
    #be thrown
    serialmonitor.after(10, SerialReadResponse)

#Exits application and kills both tkinter windows simultaneously
def exitapp():
    os._exit(0)

#Initially parse catalog file before creating any interface controls
ParseCatalogFile()

#Each group of controls and labels for both starting sky object and destination sky object is housed within its own window frame
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

#Window top menu structure
topmenu = Menu()
file = Menu(window, tearoff=0)
topmenu.add_cascade(label='File', menu=file, state='active')
serialmenu = Menu(file, tearoff=0)
file.add_cascade(label='COM Device', menu=serialmenu, state='active')
#Step through detected available serial ports and create a single dropdown menu checkbutton for only one device
for element in comlist:
    #Detect serial ports that are either Arduino or Adafruit devices
    if 'Arduino' in str(element):
        ConnectedSerialDevices.append(element.device)
        serialmenu.add_checkbutton(label=element, variable=COMPortVar, onvalue=1, offvalue=0, command=CreateSerial)
        #Only allow one COM port selectable at a time
        break
file.add_separator()
file.add_command(label='About', command=About)
file.add_separator()
file.add_command(label='Exit', command=exitapp)

window.configure(menu=topmenu)

#Begin multithreading process of simultaneously reading incoming serial data and running normal control window using the .after method
serialmonitor.after(100, SerialReadResponse)

window.mainloop()