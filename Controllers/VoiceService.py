import rpyc
import os
import time
from threading import Thread

class VoiceService(rpyc.Service):
    
    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed)
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_off(self): # this is an exposed method
        print("turn off")
        return 42

    def exposed_get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"