import os


class ScreenManager:
    
   
    screenGPIO = 252 #this is dependant on the PiTFT kernel version.  252 is for the earlier one, 508 is for the newer one
    screenIsOn = None
    
    initalized = False
    
    def initialize(self):  
        try:
            fullCommand = "sudo sh -c \"echo 'out' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/direction\""
            print(fullCommand)    
            os.system(fullCommand)      
            self.initalized = True
        except Exception:
            print("Problem initializing screen manager ")          
        
        self.screenIsOn = False
        
    def turnOn(self):
        self._changeState(1)
        self.screenIsOn = True
        
    def turnOff(self):
        self._changeState(0)
        self.screenIsOn = False
        
    def _changeState(self, state):
        if(self.initalized):
            fullCommand = "sudo sh -c \"echo '" + str(state) + "' > /sys/class/gpio/gpio" + str(self.screenGPIO) + "/value\""
            print(fullCommand)      
            os.system.Popen(fullCommand)   
        
    
    