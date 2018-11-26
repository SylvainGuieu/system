#!/Users/sylvain/anaconda3/bin/python 
from system.base2 import *
import unittest



class Sensor(System):
    _kind = "sensor"

class Sensors(Factory):
    System = Sensor
    Parameters = dict(status="off").copy

    def __ids__(self, parent):
        return range(8)

    def __make__(self, s):
        if s.id == 8 and s['room']=="living":
            raise ValueError("sensor %s has nothing to do in %r"%(s.id, s['room']))
    

class Room1(System):
    _kind = "room"
    sensors = Sensor(status="off").Factory    
    @sensors.iditerator
    def sensors(parent):
        return range(8)

    @sensors.maker
    def sensors(s):
        if s.id == 8 and s['room']=="living":
            raise ValueError("sensor %s has nothing to do in %r"%(s.id, s['room']))

class Aperture(System):
    _kind = "aperture"

    def receive(self, link):
        
        if link.kind != "light":
            return

        if self.id == "window": 
            self.parent["luminosity"] += 0.2*link["luminosity"]
        elif self.id["door"]:
            self.parent["luminosity"] += 0.1*link["luminosity"]

        self.addLink(link)

    #def send(self, link, tosystem):
    #    l = self.getLink(link)
    #    
    #    l = fromsystem.getLink("light")
    #    if l:
    #        self.recieve(tosystem, l)


class Room(System):
    Parameters = {"luminosity":0}.copy
    _kind = "room"
    sensors = Sensors()
    window = Aperture(id="window")




class House(System):
    _kind = "house"
    rooms = Room().Factory
    @rooms.iditerator
    def rooms(p):
        yield "living"
        yield "bathroom"
        yield "bedroom"

bedroom = Room(id="bedroom") 
light = Link(kind="light", luminosity=40)
print(bedroom.window.parent)
bedroom.window.receive(light)




# class Port():
    
#     def light_in(self, system, link):
#         pass

    
#     def light_out(self, system):
#         pass

#     inputs = {
#         "light":light_in
#     }
#     outputs = {
#         "lght":light_out
#     }

class LightPort(Port):
    def passive_input(self, system, link):
        if link.kind != "light":
            return 
        system.addLink(link)

    def passive_output(self, system , link):
        if link is None:
            return None   
        link.update( intensity=link.get("intensity", 0.0)*system["reflectivity"])   
        return link    


class Mirror(System):
    _kind = "mirror"
    Parameters = dict(
        reflectivity = 1.0, 
        normal = (0.0, 0.0, 0.0),
        center = (0.0, 0.0, 0.0),  
    ).copy

    light = LightPort()    


m = Mirror(id=0, reflectivity=0.86)
m.receive(Link(kind="light", intensity=4))











class Basic(unittest.TestCase):

    def test_build(self):
        house = House()

        living = house.rooms("living")
        self.assertEqual(living.sensors(1).id, 1)
        with self.assertRaises(ValueError):
            living.sensors(8)

        self.assertEqual(living.sensors(1, status="on")["status"], "on")        
        s1 = living.sensors(1)        
        self.assertEqual(living.sensors(1)["status"], "on" )
        self.assertEqual(living.sensors(2)["status"], "off")

    def test_iter(self):
        house = House()
        self.assertEqual(list(r.id  for r in list(house.rooms)), ["living", "bathroom", "bedroom"])

if __name__ == '__main__':
    unittest.main()
