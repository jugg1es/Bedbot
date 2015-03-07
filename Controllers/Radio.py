import urllib
import httplib2
import subprocess
from threading import Timer,Thread,Event

class Radio:
    
    restURL = "http://127.0.0.1:10100/"
    
    changeFrequencyTimer = None
    
    currentFrequency = 88.1
    radioProcess = None
    radioOn = False
    
    
    def startRadio(self):
        if(self.radioOn == False):
            self.radioOn = True
            print("starting RADIO")
            cmd = ['sudo', '/home/pi/startStopRadio.sh', 'start']
            subprocess.Popen(cmd)        
            #self.setFrequency(self.currentFrequency)
        
    def stopRadio(self):
        if(self.radioOn == True):
            print("stopping RADIO")
            try:
                cmd = ['sudo', '/home/pi/startStopRadio.sh', 'stop']
                subprocess.Popen(cmd)        
            except Exception:
                print("No radio process started")
            self.radioOn = False
        
        
    def setFrequency(self, freq):
        if(self.radioOn):
            if(self.changeFrequencyTimer != None):
                self.changeFrequencyTimer.cancel()
                self.changeFrequencyTimer = None
                                                   
            self.currentFrequency = freq
            self.changeFrequencyTimer =  Timer(0.6,self.doFrequencyChange) 
            self.changeFrequencyTimer.start()
    
    def doFrequencyChange(self):
        if(self.radioOn):
            if(type(self.currentFrequency) is float ):
                self.currentFrequency = str(self.currentFrequency)
            print("setting freq: " + self.currentFrequency)
            freqURL = self.restURL + "frequency/human/" +  self.currentFrequency + "M"
            self.makeCall(freqURL)
            self.changeFrequencyTimer.cancel()
            self.changeFrequencyTimer = None
        
        
    def makeCall(self, url):
        if(self.radioOn):
            try:
                h = httplib2.Http(".cache")
                h.request(url, "GET")
            except Exception:
                print("Radio server is down")
        
        
    