/*
  ParseMotorParameters.h - Library for parsing serial data input parameters for controlling a standard 1.8deg NEMA 17 stepper motor and standard 
  DC brushed motor, the input parameters are received in the following format: (motorId, motorDirection, motorSpeed(RPM), motorDegrees, holdingTorque). 
  An example is "0,1,20,320,1", which would translate to moving the stepper motor at 20RPMs counterclockwise for 177 1.8 degree steps with the holding 
  torque enabled. 
  Created by Fabian Butkovich, September, 2021.
*/
#ifndef ParseMotorParameters_h_
#define ParseMotorParameters_h_

#include "Arduino.h"

class ParseMotorParameters
{
	private:
		String input;
		float DEG_PER_SEC;
	public:
		ParseMotorParameters();
		void ParseInput(String Input);
		int ReturnMotorId();
		int ReturnMotorSpeed();
		int ReturnMotorSteps();
		int ReturnMotorDirection();
		unsigned long ReturnMotorRuntime(float DEG_PER_SEC);
		bool ReturnHoldingTorque();
};

#endif
