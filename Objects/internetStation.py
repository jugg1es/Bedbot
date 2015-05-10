class internetStation(object):
    

    id = None
    url = None
    name = None
    
    def __init__(self, json, index):
        self.id = index
        self.url = json["url"]
        self.name = json["name"]