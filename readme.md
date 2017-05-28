# overview

the system package is a box of tools to make an object oriented representation of a system defined by a flat or hierarchical data base containing system configurations. 
The two main objects are System and Collection. System describe one system and 
all the subsystems attached. Collection is used create a (sub)-system within the context of a parent system.
The use of a flat or hierarchical data base can be used to described the full System and sub system parameters. In this case the Collection is in charge of searching the database (can be anything) to get the right (sub-)system parameters. The data base is shared among system and sub-system.

# System

System can be created with class declaration or with SystemPattern function.
A System class can define the default name, the default parameters, and the Parameters dictionary like class.

    class TemperatureSensor(System):
        name = "tempsensor"
        parameters = {"status":"unknown", "unit":"K"}

is the same as:

    TemperatureSensor = System.Pattern(name="tempsensor", status="unknown", unit="K")

# Collection
the goal of Collection is to get the right system object given the parent system context.
Collection makes the link in between the data base (if any) and the system.

a Collection object must define some methods:
    - get_ids: must return a list of sub-system ids if applicable
    - get_parameters: must return a dictionary of default parameters for a given id
    - get_id: optional, in case the Collection object is called without id (or id=None) this function must return a default id if it is relevant.

the get method can also be redefined but will make the get_parameters obsolete, it can be used to make more complex behavior.

let us create first a "data base" containing the system properties:

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

Now we can create the `TempSensor` class and the `TempSensors` collection. the TempSensors Collection will be typically called from a room object

        class TempSensor(System):
            name = "tempsensor"
            @property
            def room(self):
                """ parent room """
                return self.parent("room")

        class TempSensors(Collection):
            name = "tempsensor" # name of the child system, optional
            cls = TempSensor    # class of the child system

            def get_ids(self, parent): # return a list of sensor id 
                if parent is None: # return the full list
                    for sensor in  db["tempsensors"].keys():
                        yield sensor
                    return None
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

Now we can create the room class and collection

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

And Finaly everything goes into a house:

    class House(System):
        name = "house"
        rooms = Rooms()
        @property
        def kitchen(self): # make some quick access
            """ kitchen room """
            return self.rooms("kitchen")

Use example:

        >>> house = House(db=db)
        >>> list(house.rooms)
        [<system.base.Room at 0x11077bb38 name='room' id='kitchen' >,
         <system.base.Room at 0x11077b7b8 name='room' id='living_room' >,
         <system.base.Room at 0x11077bd68 name='room' id='bed_room' >]

        >>> kitchen = house.rooms("kitchen")
        >>> lr = house.rooms("living_room")
        >>> kitchen.tempsensors() # look for a default
        <system.base.TempSensor at 0x111aac9e8 name='tempsensor' id=3 >
        >>> lr.tempsensors()
        ValueError: Their is no default sensor for room 'living_room'

        >>> list(house.rooms("living_room").tempsensors)
        [<system.base.TempSensor at 0x111b03470 name='tempsensor' id=2 >,
         <system.base.TempSensor at 0x111b030f0 name='tempsensor' id=4 >,
         <system.base.TempSensor at 0x111b03358 name='tempsensor' id=10 >]

         >>> temp = house.rooms("living_room").tempsensors(4)
         >>> temp['location']
         'window'
         >>> temp['room'] # parameters are recursive
        'living_room'
        >>> temp.room # same as temp.parent("room")
        <system.base.Room at 0x10653e780 name='room' id='living_room' >
        >>> temp.room['width']
        6
        >>> w, h =  temp.room.gets('width', 'height')

