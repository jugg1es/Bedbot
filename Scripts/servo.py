#!/usr/bin/python

import time
import pigpio
import math
from threading import Timer,Thread,Event
import sys

servo = 18


pi = pigpio.pi()
bottomRange = 700
topRange = 2500
middle = 1500
currentAngle = -1
moveSpeed = 0.02

openAngle = 60
closeAngle = 177

above90Range = topRange - middle
below90Range = middle - bottomRange


currentPulse = 0


def getAngleFromPulseWidth():
    pw = pi.get_servo_pulsewidth(servo)
    print(pw)
    if(pw == middle):
        return 90
    elif(pw >= bottomRange and pw < middle):		
        adj = float((pw - float(bottomRange))) / below90Range
        adj = adj * 90
        return int(round(adj))
    elif(pw > middle and pw <= topRange):
        adj = float((pw - float(middle))) / above90Range
        adj = (adj * 90) + 90
        return int(round(adj))


def getPulseWidth(angle):	
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
	pi.set_servo_pulsewidth(servo, mod)
	
def move(angle):
    currentAngle = getAngleFromPulseWidth()
    if(currentAngle == openAngle or currentAngle == closeAngle or currentAngle == 90):
        #print("current angle: " + str(currentAngle))
        angleDiff = currentAngle - angle
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
        
        #pi.set_servo_pulsewidth(servo,0)
        return currentAngle
    return None

def disposePigpio():
    print("stopping")
    pi.set_servo_pulsewidth(servo, 0)
    pi.stop()

setAngle(90)

move(openAngle)


def togglePosition():
    ang = getAngleFromPulseWidth()
    if(ang == openAngle):
        move(closeAngle)
    elif(ang == closeAngle):
        move(openAngle)


def cbf(gpio, level, tick):
   #print(gpio, level, tick)
   print("toggling")
   currentAngle = getAngleFromPulseWidth()
   if(currentAngle == openAngle or currentAngle == closeAngle or currentAngle == 90):
       t = Thread(target=togglePosition)
       t.start()
   

pi.set_pull_up_down(22, pigpio.PUD_DOWN)

cb1 = pi.callback(22, pigpio.RISING_EDGE, cbf)

raw_input("Press enter to end")
disposePigpio()