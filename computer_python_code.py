import cv2
from mediapipe.python.solutions import hands as mpHands
from mediapipe.python.solutions import drawing_utils as mpDraw
import math
import serial
import time


MX_MAX = 1300 # max steps fro x motor
MY_MAX =  1000 # max steps fro y motor

MAX_X = 450 # max input from the camera in x axis
MAX_Y = 400 # max input from the camera in y axis


def get_serial():
    """
    find the serial port that uses the arduino

    Returns:
        serial: the serial object
    """
    ser = 0
    for i in range(25): # check 25 ports
        try:
            ser = serial.Serial('COM'+str(i))
            print(ser.name)
            break;
        except:
            pass
    if not ser:
        print("no serial port found")
    else:
        ser.baudrate = 9600  # set Baud rate to 9600
        ser.bytesize = 8     # Number of data bits = 8
        ser.parity   ='N'    # No parity
        ser.stopbits = 1     # Number of Stop bits = 1

        print("connected to: " + ser.portstr)
        time.sleep(2)
        
    return ser


def flipPoints(x, y):
    x = -x + 500
    # y = -y + 500
    return x, y


def send_msg(ser, mx=0, my=0, s=0):
    """
    send the arduino the motor instructions
    message structure: motor1;motor2;servo    
    motor - min 50, max 500;
    servo - 0 close, 1 open; (mabe later make variable 0 - 255)
    ex. 50;200;1>
    Args:
        mx (int, optional): motor x. Defaults to 50.
        my (int, optional): motor y. Defaults to 50.
        s (int, optional): servo motor. Defaults to 0.
    """
    mx, my = flipPoints(mx, my)
    # convert input from camera position to motor steps + 50
    mx = int((MX_MAX / MAX_X) * mx + 50)  # calculated by the max ratioes (1300/500) and (1000/450)
    my = int((MY_MAX / MAX_Y) * my + 50)
    
    msg = str(mx) + ";" + str(my) + ";" + str(s) + ";>"
    print(msg)
    for chr in msg: # send the message char by char
        ser.write(chr.encode())
    

def reset(ser):
    "send the arduino the reset message (0,0,0)"
    msg = "0;0;0;>"
    print(msg)
    for chr in msg: # send the message char by char
        ser.write(chr.encode())


def findPoint(img, handLms, mpHands):
    """
    find the points of the thumb and finger in the landmarks given and draws the mesh on the image

    Args:
        img (image): the image from the camera
        handLms (list): list of the landmarks of the hand
        mpHands (object): mphands object

    Returns:
        list: list of the points of the thumb and finger and center point between them
    """
    lmList = []
    cx, cy, cz = 0, 0, 0
    # get the cuordinates of thumb and finger from list
    for id, lm in enumerate(handLms.landmark):
        if id == 4 or id == 8:
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            #  print(id, "   x: ", cx, "      y: ", cy, "      z: ", cz)
        if id == 9:
            cz = int(lm.z *-100)
        
        lmList.append([id, cx, cy, cz])
    mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)  # show dots on screen
    return lmList


def colorImage(lmlist, img):
    """
    colors the points of the thumb and finger and draws the line between them
    also colors the mid point between them and calculates the distance between them

    Args:
        lmlist (list): list of points
        img (image object): image object

    Returns:
        list: list with the mid point quordinates if the distance is smaller than 30
    """
    #  get the cuordinates of thumb and finger from list
    x1, x2 = lmlist[4][1], lmlist[8][1]
    y1, y2 = lmlist[4][2], lmlist[8][2]
    z = lmlist[9][3]

    cx, cy, cz = (x1 + x2)//2, (y1 + y2)//2, z # calculate the mid point
    #  distance calculated reletivly to the place in space with z
    dist = int(math.sqrt(math.pow(x2-x1, 2) + math.pow(y2-y1, 2)))
    if cz <= 0:
        cz = 1
    dist = int(dist / cz)
    
    point = [cx, cy]
    # draw the circles on fingers and line between
    cv2.circle(img, (x1, y1), 11, (255, 0, 0), cv2.FILLED)# thumb
    cv2.circle(img, (x2, y2), 11, (255, 0, 0), cv2.FILLED)# finger
    cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 8)# line in between
    cv2.circle(img, point, 11, (255, 0, 0), cv2.FILLED)# center point
    
    servo = 0
    if dist < 30:
        servo = 1
        cv2.circle(img, point, 11, (0, 255, 0), cv2.FILLED)# center different color

    # set boundrys by the screen size
    point[0] = 50 if (point[0] < 50) else point[0]
    point[0] = 500 if (point[0] > 500) else point[0]
    point[1] = 50 if (point[1] < 50) else point[1]
    point[1] = 450 if (point[1] > 450) else point[1]
    
    return [point, servo]


def main(ser):
    """
    main loop, gets the image from the camera then calculates distances 
    and info then sends the motor instructions to the arduino

    Args:
        ser (serial object): serial port object
    """
    while True:
        success, img = cap.read()  # read value
        img = cv2.flip(img, 1)  # mirror image
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # process image
        # process to dots
        result = hands.process(img_rgb)

        if (result.multi_hand_world_landmarks):  # if sees hand
            for handLms in result.multi_hand_landmarks:  # process for every hand
                lmlist = findPoint(img, handLms, mpHands)
                if len(lmlist) != 0:
                    # show points
                    info = colorImage(lmlist, img)
                    send_msg(ser, info[0][0], info[0][1], info[1]) # send the message to arduino
                time.sleep(0.3) # //! change if lagey (but risk of not working)
        # show the video
        cv2.imshow("Image", img)
        # exit on esc
        keyin = cv2.waitKey(1)  # wait
        if keyin == ord('q') or keyin == 27:
            break;
        



cap = cv2.VideoCapture(0)
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.8)


if __name__ == '__main__':
    ser = get_serial();
    if not ser:
        exit(0)
    
    time.sleep(1)
    reset(ser);
    
    try:
        main(ser)
    except:
        print("exiting... ")
        reset(ser);
        ser.close()

