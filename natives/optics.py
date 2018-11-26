from system.base2 import System, Input, Output
from values import *



class Mirror(System):
    Parameters = ValueDict.Pattern(
        reflectivity = Pattern(Quantified, unit="percent") 
    )
    
    input=Input()
    @input.case("light")
    def input(self, link):
        if link.kind != "light":
            return 
        self.addLink(link)

    output = Output()    
    @output.case("light")
    def output(self):
        try:
            l = self.getLink("light")
        except ValueError:
            return None
        l.instance(self, intensity=l.get("intensity", 0.0)*self["reflectivity"])




