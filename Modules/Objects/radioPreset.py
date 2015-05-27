class radioPreset(object):
    

    id = None
    frequency = None
    
    def __init__(self, json):
        self.id = json["id"]
        self.frequency = json["frequency"]