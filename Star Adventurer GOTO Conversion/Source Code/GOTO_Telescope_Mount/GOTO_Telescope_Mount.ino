/*
   This code is resposible for controlling two motors on the SkyWatcher Star Adventuer tracking mount for the purpose of converting it into a full equitorial slewing mount. The final
   mount conversion has two degrees of motion control: right acension RA and declination DEC. This source code requires the ParseMotorParameters helper library which can be found at the following
   github archive https://github.com/fbutkovich/Star-Adventurer-GOTO-Conversion

   To control the motors, a serial input string is read and parsed into five separate parameters which are formatted as follows (motor ID, motor direction, motor speed, degrees to move
   , tracking enabled). Motor ID 0 represents the RA motor, and motor ID 1 represents the DEC motor, direction is 0 for clockwise and 1 for counter-clockwise, speed is in RPMs and is ignored
   for the RA axis as it moves at a fixed speed, tracking enabled is 0 for disabled and 1 for enabled. 

   This source code is meant to be used in conjunction with the python user interface SAGOTOGUI.py, which can set a current celestial
   coordinate and destination coordinate and then compute the difference between the two and perform a telescope slew in both RA and DEC axis'
   Created by Fabian Butkovich, September, 2021.
*/

#include <Adafruit_MotorShield.h>
#include <ParseMotorParameters.h>
#include <Adafruit_PWMServoDriver.h>

#define DEBUG 1

//Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield();

/*Stepper motor with 200 steps per revolution (1.8 degree) to motor port #2 (M3 and M4) on motor driver board. This motor
  is responsible for driving the declination axis*/
Adafruit_StepperMotor *DECMOTOR = AFMS.getStepper(200, 2);

/*DC motor connected to motor port #1 (M1 and M2) on motor driver board. This motor
  is responsible for driving the right ascension axis*/
Adafruit_DCMotor *RAMOTOR = AFMS.getMotor(1);

/* Create an instance of the ParseMotorParameters class, which takes the incoming input serial string and separates it
    into five different variables used to control the behavior of the stepper motor(s)
*/
ParseMotorParameters parsemotorparameters;

//Local variables for storing motor behavior parameters returned from the parsemotorparameters class
int RASpeed;

/*Definition of physcial pins used to control two relays on the relay shield which are responsible for switching the power
  to the RA motor between the motor shield or the default Star Adventuerer driver board*/
#define RA1Relay 6
#define RA2Relay 7
/*Definition of physcial pins used to control relay on the relay shield which is responsible for toggling the direction
  the Star Adventuerer is tracking (N/S)*/
#define N_SRelay 5
#define TrackingENABLE 4

/*This constant is derived from the method described in DegreeConversion.txt and is used to convert degrees of motion
  to runtime in seconds of the RA motor*/
const float DEG_PER_SEC = 0.5;

//long positive integer for storing interval to wait before turning RA motor OFF
unsigned long runinterval;

unsigned long previousMillis = 0;
unsigned long previousMillis2 = 0;

//Boolean variables for storing state changes or if the holding torque power is enabled on the stepper motor
bool holdingTorque = false;
bool CheckRAStatus = false;

void setup()
{
  Serial.begin(115200);
  //Begin serial I2C communication with adafruit motor shield @ 800Hz
  AFMS.begin();
  /*
    if (!AFMS.begin(800)) {
    while (1);
    }
  */
  /*Setting the speed of the RA motor speed constant, this speed parameter does not directly correlate to RPM, instead
    reference DegreeConversion.txt for the steps taken to derive RPM equivalent*/
  RASpeed = 150;
  //Initialize pins for controlling two relays that switch the motor power for the Right Ascension axis to two different paths
  pinMode(RA1Relay, OUTPUT);
  pinMode(RA2Relay, OUTPUT);
  //This relay is unused but can be used if tracking direction control is desired (e.g. N/S)
  pinMode(N_SRelay, OUTPUT);
  //This relay controls the 12V power provided to the SA internal control board to either enable/disabled star tracking
  pinMode(TrackingENABLE, OUTPUT);
  digitalWrite(RA1Relay, LOW);
  digitalWrite(RA2Relay, LOW);
  //Default SA N tracking mode for northern hemisphere
  digitalWrite(N_SRelay, LOW);
  //Default enabled power to the SA
  digitalWrite(TrackingENABLE, LOW);
}

void loop()
{
  /*Use the millis() function which returns the number of milliseconds elapsed since the start of the code loop, this is used
    to calculate how long the Right Ascension motor has been on and when it should be shut off*/
  unsigned long currentMillis = millis();
  if (Serial.available() > 0)
  {
    //Read char array input from serial monitor and store it within a string datatype
    String input = Serial.readStringUntil('\n');
    /*Pass the string to the class member "ParseInput" of the parsemotorparameters class instance, which will
      retrieve the motor behavior parameters such as speed and steps to move and return a true boolean which sets the motor run state variable*/
    parsemotorparameters.ParseInput(input);
    /*If motor ID returned from "ParseInput" is 1, then run the RA motor for calculated period of time that translates to
      degrees moved*/
    if (parsemotorparameters.ReturnMotorId() == 0)
    {
      runRAmotor(currentMillis);
    }
    else
    {
      runDECmotor();
    }
#if DEBUG == 1
    debug();
#endif
  }
  //Check to see if the RA motor should be turned off by comparing the delta between currentMillis and previousMillis
  if (CheckRAStatus && currentMillis - previousMillis > runinterval)
  {
    RAMOTOR->fullOff();
    //Switch the RA motor physical connections back to the power provided by the Star Adventurer control board for accurate tracking
    digitalWrite(RA1Relay, LOW);
    digitalWrite(RA2Relay, LOW);
    /*Toggle power to the Star Adventurer control board to reset tracking after a move is performed, if tracking is
      disabled when the input serial string is given (0=disabled, 1=enabled), then the SA power will not be restored*/
    if (parsemotorparameters.ReturnTrackingEnabled() == 1)
    {
      digitalWrite(TrackingENABLE, LOW);
    }
#if DEBUG == 1
    Serial.println("OFF");
    Serial.println("------------------------------");
#endif
    CheckRAStatus = false;
  }
}

void runRAmotor(unsigned long currentMillis)
{
  //Switch the RA motor physical connections to the power provided by the Adafruit motor shield for fast slewing
  digitalWrite(RA1Relay, HIGH);
  digitalWrite(RA2Relay, HIGH);
  //Toggle power to the Star Adventurer control board to reset tracking after a move is performed
  digitalWrite(TrackingENABLE, HIGH);
  //Set the runtime in seconds for the RA motor
  runinterval = parsemotorparameters.ReturnMotorRuntime(DEG_PER_SEC);
  //Restart the non-blocking millis() timer which is used to check how long the RA motor has been running
  previousMillis = currentMillis;
  //Setting the speed of the RA motor
  RAMOTOR->setSpeed(RASpeed);
  RAMOTOR->run(parsemotorparameters.ReturnMotorDirection());
  CheckRAStatus = true;
}

void runDECmotor()
{
  DECMOTOR->setSpeed(parsemotorparameters.ReturnMotorSpeed());
  DECMOTOR->step(parsemotorparameters.ReturnMotorSteps(), parsemotorparameters.ReturnMotorDirection(), DOUBLE);
  DECMOTOR->release();
}

#if DEBUG == 1
//This function prints debugging information
void debug()
{
  //Retrieve debugging info
  if (parsemotorparameters.ReturnMotorId() == 1)
  {
    Serial.println("Motor: DEC");
    Serial.print("Speed: ");
    Serial.print(parsemotorparameters.ReturnMotorSpeed());
    Serial.println("RPM");
    if (parsemotorparameters.ReturnMotorDirection() == 1)
    {
      Serial.println("Direction: CW");
    }
    else if (parsemotorparameters.ReturnMotorDirection() == 2)
    {
      Serial.println("Direction: CCW");
    }
    Serial.print("Motor Steps: ");
    Serial.println(parsemotorparameters.ReturnMotorSteps());
    Serial.print("Normal Tracking Enabled?: ");
    Serial.println(parsemotorparameters.ReturnTrackingEnabled());
  }
  else if (parsemotorparameters.ReturnMotorId() == 0)
  {
    Serial.println("Motor: RA");
    Serial.print("Speed: ");
    Serial.print(5886);
    Serial.println("RPM");
    if (parsemotorparameters.ReturnMotorDirection() == 1)
    {
      Serial.println("Direction: CW");
    }
    else if (parsemotorparameters.ReturnMotorDirection() == 2)
    {
      Serial.println("Direction: CCW");
    }
    Serial.print("Motor Runtime: ");
    Serial.print(runinterval);
    Serial.println("ms");
    Serial.print("Normal Tracking Enabled?: ");
    Serial.println(parsemotorparameters.ReturnTrackingEnabled());
  }
  Serial.println("------------------------------");
}
#endif
