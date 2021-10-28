/*
  ParseMotorParameters.h - Library for parsing serial data input parameters for controlling a standard 1.8deg NEMA 17 stepper motor and standard 
  DC brushed motor, the input parameters are received in the following format: (motorId, motorDirection, motorSpeed(RPM), motorDegrees, holdingTorque). 
  An example is "0,1,20,320,1", which would translate to moving the stepper motor at 20RPMs counterclockwise for 177 1.8 degree steps with the holding 
  torque enabled. 
  Created by Fabian Butkovich, September, 2021.
*/
#include "Arduino.h"
#include "ParseMotorParameters.h"

int index = 0;
//Array to store positions of delimiter characters
int delimiterPos[4];

String numbers[5] = {"", "", "", "", ""};

ParseMotorParameters::ParseMotorParameters()
{
}

void ParseMotorParameters::ParseInput(String input)
{
  //Reset the input string,
  for (int x = 0; x < 5; x++) 
  {
    numbers[x] = "";
  }
  index = 0;
  //Step through string and retrieve positon of each delimiter, assign the position number to the current delimiter# 1-3
  for (int i = 0; i < input.length(); i++) 
  {
    if (input[i] == ',') 
	{
      delimiterPos[index] = i;
      index++;
    }
  }
  //Append number string 1 with all the characters in the input string before the first delimiter
  for (int i = 0; i < delimiterPos[0]; i++) 
  {
    if (input[i] != ',') 
	{
      numbers[0] += input[i];
    }
  }
  //Append number string 2 with all the characters in the input string after the first delimiter
  for (int i = delimiterPos[0]; i < delimiterPos[1]; i++) 
  {
    if (input[i] != ',') 
	{
      numbers[1] += input[i];
    }
  }
  //Append number string 3 with all the characters in the input string after the second delimiter
  for (int i = delimiterPos[1]; i < delimiterPos[2]; i++) 
  {
    if (input[i] != ',') 
	{
      numbers[2] += input[i];
    }
  }
  //Append number string 4 with all the characters in the input string after the third delimiter
  for (int i = delimiterPos[2]; i < delimiterPos[3]; i++) 
  {
    if (input[i] != ',') 
	{
      numbers[3] += input[i];
    }
  }
  //Append number string 5 with all the characters in the input string after the fourth delimiter
  for (int i = delimiterPos[3]; i < input.length(); i++) 
  {
    if (input[i] != ',') 
	{
      numbers[4] += input[i];
    }
  }
}

int ParseMotorParameters::ReturnMotorId()
{
  //Only accept a 0 or 1 for motor Id input, motor ID 0 represents the stepper motor for control of the DEC axis, and ID 1 is for the RA motor
  if (numbers[0] == "0" || numbers[0] == "1")
  {
    return numbers[0].toInt();
  }
  else
  {
    return 0;
  }
}

int ParseMotorParameters::ReturnMotorSpeed()
{
  return numbers[2].toInt();
}

//Input degrees to move must be multiplied by 122 since the gear reduction of the declination worm wheel is 122:1, the C++ function "toFloat()" is used since we need 1/10th of a degree precision
int ParseMotorParameters::ReturnMotorSteps()
{
  return (numbers[3].toFloat() * 122) / 1.8;
}

//This function accepts a known constant "DEG_PER_SEC" and uses it to convert degrees of motion to runtime in seconds of the RA motor, the C++ function "toFloat()" is used since we need 1/10th of a degree precision
unsigned long ParseMotorParameters::ReturnMotorRuntime(float DEG_PER_SEC)
{
  return (numbers[3].toFloat() / DEG_PER_SEC) * 1000;
}

int ParseMotorParameters::ReturnMotorDirection()
{
  if (numbers[1] == "1")
  {
    //Counter-clockwise rotation
    return 2;
  }
  else if (numbers[1] == "0")
  {
    //Clockwise rotation
    return 1;
  }
  else
  {
    return 0;
  }
}

bool ParseMotorParameters::ReturnHoldingTorque()
{
  if (numbers[4].toInt() == 1)
  {
    return true;
  }
  else
  {
    return false;
  }
}