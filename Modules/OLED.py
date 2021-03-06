
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

import datetime
from Helpers.perpetualTimer import perpetualTimer
from threading import Timer,Thread,Event
import time

libarariesLoaded = False

try:    
    import Adafruit_GPIO.SPI as SPI
    import Adafruit_SSD1306
    
    libarariesLoaded = True
except ImportError:
    print('Adafruit gpio spi Adafruit_SSD1306 library not found')
    
try:    
    import Image
    import ImageDraw
    import ImageFont
except ImportError:
    print('Image libraries not found')




class OLED(QObject):

    Enabled = True    
    ListenForPinEvent = False

    pinRST = None
    pinCS = None    
    pinCLK = None
    pinDC = None
    pinDIN = None


    thread = None
    oledUpdateTimer = None
    previousTime = "0"

    def __init__(self):
        super(OLED, self).__init__()

    def setPin(self, pinConfig):
        self.pinRST = pinConfig["OLED_RST"]
        self.pinCS = pinConfig["OLED_CS"]
        self.pinCLK = pinConfig["OLED_CLK"]
        self.pinDC = pinConfig["OLED_DC"]
        self.pinDIN = pinConfig["OLED_DIN"]
        self.initialize()


    def initialize(self):        
        if(libarariesLoaded):
            self.oledUpdateTimer = perpetualTimer(5, self.handle_function)
            self.oledUpdateTimer.start()
        else:
            print("Adafruit OLED libraries not found")
        


    def handle_function(self):
        #print(self.previousTime)
        t = Thread(target=self._doUpdateTime, args=(self,))        
        t.start()
        '''
        if(self.previousTime == "0"):
            self.previousTime = self.updateTime(self.previousTime, self.pinRST, self.pinCS, self.pinCLK, self.pinDC, self.pinDIN)
            time.sleep(0.1)
        self.previousTime = self.updateTime(self.previousTime, self.pinRST, self.pinCS, self.pinCLK, self.pinDC, self.pinDIN)
        '''


    def dispose(self):
        if(self.oledUpdateTimer != None):
            self.oledUpdateTimer.cancel()

    def _doUpdateTime(self, parent):
        #print("doupdatetime")
        parent.previousTime = self.updateTime(parent.previousTime, parent.pinRST, parent.pinCS, parent.pinCLK, parent.pinDC, parent.pinDIN)

    def updateTime(self, previousTime, RST, CS, CLK, DC, DIN):
        

        n = datetime.datetime.now()
        timeString = n.strftime("%I:%M").lstrip("0")

        if(libarariesLoaded == False):
            return timeString

        if(timeString != previousTime):
            # Raspberry Pi pin configuration:
            #RST = 21
            # Note the following are only used with SPI:
            #DC = 20
            #SPI_PORT = 0
            #SPI_DEVICE = 0
            '''
            RST = 21
            CS = 20
            CLK = 19
            DC = 16
            DIN = 13
            '''
            # Beaglebone Black pin configuration:
            # RST = 'P9_12'
            # Note the following are only used with SPI:
            # DC = 'P9_15'
            # SPI_PORT = 1
            # SPI_DEVICE = 0
            
            # 128x32 display with hardware I2C:
            #disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)
            
            # 128x64 display with hardware I2C:
            # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
            
            # Note you can change the I2C address by passing an i2c_address parameter like:
            # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
            
            # Alternatively you can specify an explicit I2C bus number, for example
            # with the 128x32 display you would use:
            # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, i2c_bus=2)
            
            # 128x32 display with hardware SPI:
            # disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
            
            # 128x64 display with hardware SPI:
            # disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))
            
            # Alternatively you can specify a software SPI implementation by providing
            # digital GPIO pin numbers for all the required display pins.  For example
            # on a Raspberry Pi with the 128x32 display you might use:
            disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST, dc=DC, sclk=CLK, din=DIN, cs=CS)
            
            # Initialize library.
            disp.begin()
            
            # Clear display.
            #disp.clear()
            #disp.display()
            
            # Create blank image for drawing.
            # Make sure to create image with mode '1' for 1-bit color.
            width = disp.width
            height = disp.height
            
            image = Image.new('1', (width, height))
            padding = 2
            x=padding
            
            top = 0
            bottom = height-padding
            
            availableWidth = width - (padding*2) - 10
        
            # Get drawing object to draw on image.
            draw = ImageDraw.Draw(image)            
            
            font = ImageFont.truetype("VCR_OSD_MONO.ttf", 35)
            
            size = draw.textsize(timeString, font)
            
            location = (width / 2) - (size[0] /2)
            
            # Write two lines of text.
            draw.text((location, top),    timeString,  font=font, fill=255)
            
            # Display image.
            disp.image(image)
            disp.display()
        return timeString
