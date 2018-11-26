"""package to define an object oriented representation of a system. 

The package provides two mains classes :class:`System` and :class:`Collection`.

A System instance carries two things:

- Pairs of keys/ values that define configuration, state, etc ...
- A set of Collection instance that define how to create sub-systems within the 
    context of the parent system

The goal of Collection instance is to build a new system within the context of the parent 
    object.

Collection object can use a database (which can be anything) to build a new system or subsystem.
The Collection object are intended to be subclassed by user pre-defined object that link the 
created sub-system to the optional database and the parent system

Each system instance are considered as unique if they share:

- the same parent 
- the same `kind` (typically a string)
- the same `id`   (typically a string or integer)
- the same `link` (a Link object or string)

`link` represent the type of link between a sub-system and its parent, for instance it can be
"light" (connection in between 2 mirrors), "electrical", "physical", etc... Can be None also 

Quick Example
=============
::  

    class Rooms(Collection):
        kind = "room" # kind of the created System
        
        def init(self, s): # init the newly build room system instance            
            if s.id is None:
                raise ValueError("Their is no default room")
            
            try:
                p = s.db[s.id]
            except KeyError:
                raise ValueError('room %s does not exists'%s.id)
            
            for k,v in p.items():
                s.setdefault(k,v)
        
        def iterids(self, parent, kind, link):
            return self.db.keys()

    
    rooms = Rooms(db= {
                        'living-room': {'width':12, 'height':5.2}, 
                        'bed-room'   : {'width':4, 'height':3.1}    
                    }
                )
    
    house = System(kind="house", id="my house")
    bedroom = rooms(id='bed-room', parent=house)


Also one can reclass the House and Room System::
    
    class Room(System):
        kind = "room"
    
    Rooms.System = Room # this is now the default System constructor for Rooms
    
    class House(System):
        kind = "house"
        rooms = Rooms(db= {
                        'living-room': {'width':12, 'height':5.2}, 
                        'bed-room'   : {'width':4, 'height':3.1}    
                    }
                )
    
    >>> myhouse = House(id="my house")
    >>> myhouse.rooms('living-room')['width']
    12
    
    >>> size_list = list( (room['width'], room['height']) for room in myhouse.rooms  )
    
    >>> bedroom = myhouse.rooms('bed-room')
    >>> bedroom.parent
    <system.base.House at 0x10b7935c0 kind='house' id='my house' >

If you know that all your houses have a living-room you can add a property::

    class House(System):
        kind = "house"
        rooms = Rooms(db= {
                        'living-room': {'width':12, 'height':5.2}, 
                        'bed-room'   : {'width':4, 'height':3.1}    
                    }
                )
        livingroom = rooms.Property("living-room")
    


    >>> myhouse = House(id="my house")
    >>> myhouse.livingroom
    <system.base.System at 0x1084399b0 kind='room' id='living-room' >
    >>> myhouse.livingroom.parent
    <system.base.House at 0x10b7935c0 kind='house' id='my house' >
    
In the same fashion one can use the ParentProperty ::
    
    ##
    # will return the parent of kind house 
    >>> Room.house = House.ParentProperty()
    
    >>> bedroom = House(id="my house").rooms("bedroom")
    >>> bedroom.house
    <system.base.House at 0x10b7935c0 kind='house' id='my house' >
    

Important behavior about key/value pairs inside a system
--------------------------------------------------------

like a dictionary object System object has the getitem and setitem methods





.. moduleauthor:: Sylvain Guieu <sylvain.guieu@gmail.com>

"""
from .base import Documents, Document
from .base import System, Port, Factory, SystemProperty, query, action, Link, issystem, port, DEFAULT
from .base import View, view
#__all__ = ["System", "Collection", "Link", "ParentProperty"]
