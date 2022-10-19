/*
19/10/2022
created by matanton
*/


#include <Stepper.h>
#include <Servo.h>

#define STEPS 2040
// motors, change the pins according to yours
Stepper mx(STEPS, 12, 10, 11, 9); // motor x
Stepper my(STEPS, 5, 3, 4, 2); // motor y

Servo servo;
// motor constants

const int STEPS_PER_TIME = 100;

const int SERVO_PIN = 6; // change according to yours
const int SERVO_MIN = 70;
const int SERVO_MAX = 150;

const int M_MID = 180; // middle man where all movement is free (motor_middle)
const int MIN = 50; // min input steps amount from serial

// other parameters
int pos = 0;

long lastPos[2] = {MIN, MIN}; // initial position of the motors
long wantedPos[3] = {MIN, MIN, 0};
int* moved = new int[2];

String read = " ";
String param = " ";
char input = ' ';



void setup() {
	servo.attach(SERVO_PIN);
	Serial.begin(9600);
	mx.setSpeed(18); // set the speed of the motor (recommended 5-25)
	my.setSpeed(18);
	delay(100);
	moved[0] = MIN;
	moved[1] = MIN;
}



// turns the motors off so they wont warm up to fast
void deactivate()
	{
	for (int i = 9; i <= 12; i++)
	{
	digitalWrite(i, LOW); // mx
	digitalWrite((i - 12) + 5, LOW); // my
	}
	}


/**
 * @brief calculates the needed steps for the motor to make to get to a certain position
 * 
 * @param x the wanted x position
 * @param y the wanted y position
 * @param s the wanted servo position
 * @param lastX the current position of the x motor
 * @param lastY the current position of the y motor
 */
void move_motor(long x, long y, int s, int lastX, int lastY){
	// check if the motors are at free movment or limited (less than mid)
	if (y < M_MID && x > M_MID) x = (float)M_MID;
	if (x < M_MID && y > M_MID) y = (float)M_MID;

	// get how mutch to move
	x -= lastX;
	y -= lastY;

	Serial.print(x); // print the current position of the motors
	// Serial.print("  :  "); // for debuging
	// Serial.print(y);
	// Serial.print("  ->  ");

	// move servo
	s ? servo.write(SERVO_MIN) : servo.write(SERVO_MAX);

	// turn the amount of steps to the STEPS_PER_TIME or less 
	if (x > STEPS_PER_TIME) x = STEPS_PER_TIME;
	if (y > STEPS_PER_TIME) y = STEPS_PER_TIME;

	// move motors
	mx.step(-x);
	my.step(-y);
	// deactivate(); // uncomment if want more time without motors heating up but can be more laggy

	moved[0] = x;
	moved[1] = y;// store how much the motors moved
}


/**
 * @brief parse a string of istructions to an array (the wantedPos array)
 * 
 * @param read the string to parse
 */
void extractInstructions(String read){
	for(int i = 0; i < 3; i++){ // get the number parts one by one, parse it then turn to number 
		int index = read.indexOf(";");
		param = read.substring(0, index); // slice
		read = read.substring(index + 1); // remove
		wantedPos[i] = param.toInt();
	}
}


/**
 * @brief reads from the serial port, get the message char by char and combine it to string
 * then parse it into an array
 */
void readSerial(){
	while(input < 60){
	input = Serial.read();
	read += input;
	delay(10);
	}
	// check if read someting and remove the ">" from end of string
	if (read){
		read = read.substring(0, read.length() - 1);
		extractInstructions(read);
	}
}



	// 100;100;0;>   -   example of a command from the computer to the arduino
void loop() { // main loop
	read = " ";
	param = " ";
	input = ' ';

	delay(10);
	if (Serial.available()) 
	{
		readSerial();
		Serial.end(); // do this to prevent serial port bugs
		Serial.begin(9600);
	}
	else if (lastPos[0] != wantedPos[0] || lastPos[1] != wantedPos[1]){ // check if the motors need to move
		// move from the current postition + MOVE_STEPS steps to the wanted position
		// if no input then move the motor closer to the wanted position 
		move_motor(wantedPos[0], wantedPos[1], wantedPos[2], lastPos[0], lastPos[1]);
		lastPos[0] += moved[0]; // update new position
		lastPos[1] += moved[1];
	}
	else{
		deactivate();
	}
}
