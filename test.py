#!/Users/sylvain/anaconda3/bin/python 
from system import *


db = {
    "rooms" :{
        "kitchen": {"width":4, "height":3, "tempsensors":[3]},
        "living_room": {"width":6, "height":4.5, "tempsensors":[2,4,10]},
        "bed_room": {"width":2, "height":2, "tempsensors":[]}
    },
    "tempsensors" : {
        3 :  {"type":"pt100", "unit":"k", "location":"roof"},
        2  : {"type":"pt100", "unit":"k", "location":"roof"},
        4  : {"type":"pt100", "unit":"k", "location":"window"},
        10 : {"type":"pt100", "unit":"k", "location":"floor"}
    }
}


class TempSensor(System):
    name = "tempsensor"
    @property
    def room(self):
        return self.parent("room")


class TempSensors(Collection):
    name = "tempsensor" # name of the child system, optional
    cls = TempSensor    # class of the child system

    def get_ids(self, parent): # return a list of sensor id 
        if parent is None: # return the full list
            for sensor in  db["tempsensors"].keys():
                yield sensor

        room = parent.get("room", None)
        if room is None:
            raise ValueError("No room information")

        roomInfo = parent.db["rooms"][room]
        for sensor, sensorInfo in db["tempsensors"].items():
            if sensor in roomInfo['tempsensors']:
                yield sensor

    def get_parameters(self, parent, id):
        return parent.db["tempsensors"][id]

    def get_id(self, parent): # called if id is None
        room = parent.get("room", None)
        if room is None:
            raise ValueError("No room information")
        sensors = parent.db["rooms"][room]['tempsensors']
        if len(sensors)!=1:
            raise ValueError("Their is no default sensor for room %r"%room)
        return sensors[0]


class Room(System):
    name = "room"
    tempsensors = TempSensors() # this is the sensor query object

class Rooms(Collection):
    cls = Room
    def get_ids(self, parent):
        db = db if parent is None else parent.db
        return db['rooms'].keys()
    def get_parameters(self,parent, id):
        db = db if parent is None else parent.db
        return db['rooms'][id]


class House(System):
    name = "house"
    rooms = Rooms()
    @property
    def kitchen(self): # make some quick access
        """ kitchen room """
        return self.rooms("kitchen")

house = House(db=db)
print(list(house.rooms))
kitchen = house.rooms("kitchen")
print(kitchen.tempsensors())

temp = house.rooms("living_room").tempsensors(4)
temp['location']
   
temp['room'] # parameters are recursive
