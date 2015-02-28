from threading import Thread
import atexit, socket, time, subprocess
from _csv import Error
from PyQt4.QtCore import QObject
from PyQt4 import QtCore
from enum import Enum


pianobarUseable = True

class PandoraCommand(Enum):
    NONE = 0
    STOP =1
    PLAY = 2
    CHANGESTATION =3
    SKIPSONG = 4
    KILL = 5


try:
    import pexpect, pickle
except ImportError:
    pianobarUseable = False
    print('PExpect or pickle library not found')
    
class Pandora(QObject):
    pandoraOn = False
    stationList = []
    stationsIDs = []
    
    initialized = False
    currentStation = None
    pianobar = None
    
    killing = False
    
    cmd = PandoraCommand.NONE
    
    
    PICKLEFILE = '/home/pi/.config/pianobar/state.p'
    
    def __init__(self):
        super(Pandora, self).__init__()
        self.initalized = False    
        
        atexit.register(self.stopPandora)
        self.t = Thread(target=self.initializePianobar, args=(self,))
        self.t.start()
        
    def isInitialized(self):
        if(self.initalized):
            return True
        return False
        
    def initializePianobar(self, parent):
        if(pianobarUseable):
            try:
                print('Spawning pianobar...')
                parent.pianobar = pexpect.spawn('sudo -u pi pianobar')
                print('Receiving station list...')
                parent.pianobar.expect('Get stations... Ok.\r\n', timeout=30)
                parent.stationList, parent.stationIDs = parent.getStations(parent.pianobar)       
                print('Station List Recieved')
            
                f = open(parent.PICKLEFILE, 'rb')
                v = pickle.load(f)
                f.close()
                parent.currentStation = v[0]
                parent.initalized = True
                parent.emit(QtCore.SIGNAL('pandoraInitialized'))  
            except:
                parent.currentStation = None
                parent.pianobar.kill(0)
            
        
        
    
    
    def setStation(self, stationName):
        print("starting: " + stationName)
        self.currentStation = stationName
        self.launchPianobar()
        
    def launchPianobar(self):
        self.pianothread = Thread(target=self.spinupPianobar, args=(self,))
        self.pianothread.start()
        
    def spinupPianobar(self, parent):
        pianobar = parent.pianobar
        '''print('Spawning pianobar...')
        pianobar = pexpect.spawn('sudo -u pi pianobar')
        print('Receiving station list...')
        pianobar.expect('Get stations... Ok.\r\n', timeout=30)
        stationList, stationIDs = self.getStations(pianobar)
        try:    # Use station name from last session
            stationNum = stationList.index(parent.currentStation)
        except: # Use first station in list
            stationNum = 0
        print 'Selecting station ' + stationIDs[stationNum]'''
        
        stationNum =0
        
        for i in range(0, len(parent.stationList)):
            print(parent.stationList[i])
            if(parent.stationList[i] == parent.currentStation):
                stationNum = i
        
        pianobar.sendline(parent.stationIDs[stationNum])
        
        lastTime = 0
        
        pattern_list = pianobar.compile_pattern_list(['SONG: ', 'STATION: ', 'TIME: '])
        
        print(PandoraCommand(parent.cmd));
        while pianobar.isalive():
        
            # Process all pending pianobar output
            while True:
                
                try:
                    x = pianobar.expect(pattern_list, timeout=0)
                    if x == 0:
                        songTitle  = ''
                        songInfo   = ''
                        xTitle     = 16
                        xInfo      = 16
                        xTitleWrap = 0
                        xInfoWrap  = 0
                        x = pianobar.expect(' \| ')
                        if x == 0: # Title | Artist | Album
                            s = pianobar.before + '    '
                            n = len(s)
                            xTitleWrap = -n + 2
                            # 1+ copies + up to 15 chars for repeating scroll
                            songTitle = s * (1 + (16 / n)) + s[0:16]
                            x = pianobar.expect(' \| ')
                            if x == 0:
                                artist = pianobar.before
                                parent.emit(QtCore.SIGNAL('pandoraSongChange'), artist, s)  
                                x = pianobar.expect('\r\n')
                                if x == 0:
                                    print ('Album: "{}"'.format(pianobar.before))
                                    s = artist + ' < ' + pianobar.before + ' > '
                                    n = len(s)
                                    xInfoWrap = -n + 2
                                    # 1+ copies + up to 15 chars for repeating scroll
                                    songInfo  = s * (2 + (16 / n)) + s[0:16]
                    elif x == 1:
                        x = pianobar.expect(' \| ')
                        if x == 0:
                            print ('Station: "{}"'.format(pianobar.before))
                    elif x == 2:
                        # Time doesn't include newline - prints over itself.
                        x = pianobar.expect('\r', timeout=1)
                        if x == 0:
                            print ('Time: {}'.format(pianobar.before) + " " + parent.cmd)
                        # Periodically dump state (volume and station name)
                        # to pickle file so it's remembered between each run.
                        try:
                            f = open(parent.PICKLEFILE, 'wb')
                            pickle.dump([parent.stationList[stationNum]], f)
                            f.close()
                        except:
                            pass    
                        
                    print(parent.cmd != PandoraCommand.NONE)
                    if(parent.cmd != PandoraCommand.NONE):
                        break;                    
                except pexpect.EOF:
                    break
                except pexpect.TIMEOUT:
                    break
                    
            if(parent.cmd == PandoraCommand.KILL):
                break
            elif(parent.cmd == PandoraCommand.STOP):
                print("stop hit")
                pianobar.send('p')
                pianobar.send(' ')
                parent.cmd = PandoraCommand.NONE
            
            
        if(parent.cmd == PandoraCommand.KILL):
            pianobar.send('p')
            pianobar.send('q')            
            parent.shutdown(parent)
       
            
    

    def shutdown(self,parent):
        parent.pianobar.kill(0)
        
        
                
    def stopPandora(self):        
        self.cmd = PandoraCommand.STOP
            
            
    def getStations(self, pb):   
        pb.expect('Select station: ', timeout=10)
        # 'before' is now string of stations I believe
        # break up into separate lines
        a     = pb.before.splitlines()
        names = []
        ids   = []
        # Parse each line
        for b in a[:-1]: # Skip last line (station select prompt)
            # Occasionally a queued up 'TIME: -XX:XX/XX:XX' string or
            # 'new playlist...' appears in the output.  Station list
            # entries have a known format, so it's straightforward to
            # skip these bogus lines.
    #        print '\"{}\"'.format(b)
            if (b.find('playlist...') >= 0) or (b.find('Autostart') >= 0):
                continue
    #        if b[0:5].find(':') >= 0: continue
    #        if (b.find(':') >= 0) or (len(b) < 13): continue
            # Alternate strategy: must contain either 'QuickMix' or 'Radio':
            # Somehow the 'playlist' case would get through this check.  Buh?
            if b.find('Radio') or b.find('QuickMix'):
                id   = b[5:7].strip()
                name = b[13:].strip()
                # If 'QuickMix' found, always put at head of list
                if name == 'QuickMix':
                    ids.insert(0, id)
                    names.insert(0, name)
                else:
                    ids.append(id)
                    names.append(name)
        return names, ids
    
    def dispose(self):
        self.cmd = PandoraCommand.KILL

        
    
        
    