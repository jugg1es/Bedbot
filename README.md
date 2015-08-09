# Bedbot #

##Introduction ##
Bedbot is an embedded Alarm/Clock/Radio application for Raspberry Pi for use in customized bed-side table written in Python.  

It is designed so that modules can be integrated without having to touch the core application code at all.  The core application gives modules access to all of the other components and GPIO pins without having to know anything about the other modules.  It is a way to build touchscreen-enabled GUI applications that can control anything you can plug into a Raspberry Pi.

Designed to be displayed on [320x240 TFT+Touchscreen](https://www.adafruit.com/products/1601) with several buttons for control.

Here is the full hardware write-up:  [http://www.peterroca.com/bedbot](http://www.peterroca.com/bedbot)

<img src="http://peterroca.com/bedbot/assets/img/main.jpg" width="320" height="240" />

<img src="http://peterroca.com/bedbot/assets/img/topCloseupOpen.jpg" width="320" height="240" />


##Prerequisites ##

* Python 2.7
* [PyQT4](http://www.riverbankcomputing.com/software/pyqt/download)
* [PIGPIO](http://abyz.co.uk/rpi/pigpio/)

###Optional libraries ###
* [MPC/MPD](http://www.musicpd.org/clients/mpc/)
* [RTL_FM_PYTHON](https://github.com/th0ma5w/rtl_fm_python)


##Included Modules ##
* [Persistant clock display (via OLED)](Modules/OLED.py)
* Programmable Alarm Clock
* FM radio tuner
* Internet Radio Streaming
* Audio Input Source switch
* Servo controller

