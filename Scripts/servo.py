#!/usr/bin/python

import time
import pigpio
import math
import sys

servo = 18

pi = pigpio.pi()
bottomRange = 700
topRange = 2500
middle = 1500
currentAngle = -1
moveSpeed = 0.02


def getAngleFromPulseWidth():
    print(pi.get_servo_pulsewidth(servo))


def getPulseWidth(angle):
	above90Range = topRange - middle
	below90Range = middle - bottomRange
	mod = middle
	if(angle > 90 and angle <= 180):		
		percent = float((angle - 90)) / 90
		mod = math.trunc(middle + (float(percent) * above90Range))
	elif(angle < 90 and angle >= 0):
		percent = float(angle) / 90
		mod = math.trunc(bottomRange + (float(percent) * below90Range))
	return mod

def setAngle(angle):
	mod = getPulseWidth(angle)
	
	#print("setting to: " + str(mod))
	pi.set_servo_pulsewidth(servo, mod)
	
def move(angle):
	#print("currentAngle: " + str(currentAngle))

	angleDiff = currentAngle - angle
	#print("diff: " + str(angleDiff))
	angleTracker = currentAngle
	angleDir = 0
	if(angleDiff < 0):
		angleDir = 1
	elif(angleDiff > 0):
		angleDir = -1
	for angle in range(abs(angleDiff)):		
		angleTracker += angleDir		
		setAngle(angleTracker)	
		time.sleep(moveSpeed)
	pi.set_servo_pulsewidth(servo,0)
	return angleTracker

#setAngle(90)
#currentAngle = 90

print("command: " + sys.argv[1])
print(sys.argv)
if(len(sys.argv) >= 2):
    if(sys.argv[1] == "init"):
        setAngle(90)
    elif(sys.argv[1] == "open"):
        #move(60)
        getAngleFromPulseWidth()
        setAngle(60)
    elif(sys.argv[1] == "close"):
        getAngleFromPulseWidth()
        setAngle(175)
        #move(175)




'''
raw_input("Enter to move")
print("currentAngle: " + str(currentAngle))
currentAngle = move(175)

raw_input("Enter to move")
print("currentAngle: " + str(currentAngle))
currentAngle = move(60)

raw_input("Enter to end")
'''


pi.set_servo_pulsewidth(servo, 0)

pi.stop()
