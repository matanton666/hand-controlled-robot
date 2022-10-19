# hand-controlled-robot

This is a 2 axis robot that is controlled by the position of your hand that is captured by a camera.  
[example use video](https://youtu.be/Lk0FQm9ZR9w)
Robot is controlled by an arduino uno and a computer with a camera.  
  
![Image of the robot](/media/side%20view.jpg)
  
---
  
## Parts

- 1 3d printer
- 1 servo motor
- 2 stepper motors (28BYJ-48)
- 1 Arduino Uno
- 1 breadboard
- 1 power supply (9v-12v)
  
## setup
  
### 3d printing
  
[heres a link to the 3d models](https://www.thingiverse.com/thing:2838859)
I printed the parts with a 0.2mm layer height and 20% infill.  
>there is no nead for the third motor in the botom because there is no use for the third axis.
  
### instructions

> I recommend to do this in a virtual environment with python.
1. Run the dependencies.sh file to install the dependencies.
2. Upload the arduino code to the arduino.
3. configure the constant variables in the python and arduino code to your needs.
4. run the arduino then the python code, and you should be good to go.
  
---
## scematics and sutch:
#### connection scematics:
connect the 2 motors to the drivers and connect the power supply to the drivers.
connect the drivers and the servo to the arduino.
beware of the pins you put the motors and servo on.  
![Image of circuit](/media/circuit.png)
  
![Image of robot up](/media/up%20view.jpg)