# Star-Adventurer-GOTO-Conversion
Source code, schematics and 3D printing files for the conversion of the SkyWatcher Star Adventurer to a full GOTO equatorial telescope mount. The conversion will require soldering skills in order to splice the yellow and blue wires from the 
brushed DC motor inside the stock SA. The current version of the Python GUI was developed with Python 3.9. The included "Adafruit_Motor_Shield_V2_Library" MUST be used vs. the default version available to the public, as it was modified to 
support accurate stepper motor stepping. The helper library "ParseMotorParameters" must also be placed inside the C:\Users\username\Documents\Arduino\libraries folder if modifying/re-uploading the source code. 

![image](/assets/images/thumbnail.jpg)