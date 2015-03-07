import rpyc
from Controllers import VoiceService
import threading

from rpyc.utils.server import OneShotServer
from rpyc.utils.server import ThreadedServer  


class Communicate:
    
    conn = None
    
       
    def startServer(self):
        self.s = ThreadedServer(VoiceService, port = 12345)
        self.t = threading.Thread(target=self.s.start)
        self.t.start()
        
        print("starting server")
              
        
    def start(self):      
        print("starting server")
        self.t.start()
        
        
    def sendCommand(self):
        print("sending command")
        #print(rpyc.discover("VOICE"))
        c = rpyc.connect("127.0.0.1", 12345)
        print(c.root.get_service_aliases())
        print(c.root.get_service_name())
        answer = c.root.off()
        print(answer)
        
    def stopServer(self):
        print("stoppinf")
        self.s.close()
        
                 
