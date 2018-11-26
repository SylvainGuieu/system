from system import Factory, System
from values.base import Value,  ParamsView
from values import ValueDict
from utils.info import info

import dash_core_components as dcc
import dash_html_components as html



@Value.__info__.case("dash")
def __info__(self, depth):

    return html.Div(
         [  
            html.Div("computed value" if getattr(self, "__computed__", None) else info(self.get(), "dash", depth))
         ]+[info(self.params,"dash", depth-1)]
        )

@ParamsView.__info__.case("dash")
def __info__(self, depth):
    return html.Ul(
        [
         html.Li(
            ".{key}: {value}".format(key=k, value=self[k])
            ) for k in self.keys()
        ]
    )

@ValueDict.__info__.case("dash")
def __info__(self, depth):
    if depth == 0:
        return html.Div()
    depth -= 1
    out = []

    for k in self.keys():
        out.append(

                
                html.Li([
                        html.Div(info(k, "dash")), 
                        info(self[k,], "dash", depth)
                        ]
                    )
            )
    return html.Ul(out)


@System.__info__.case("dash")
def __info__(self, depth):
    path =  self.getAbsolutePath()

    subsystems = [html.A(children=f.kind+" ", href="/"+path+"/"+f.kind) for f in self.factories()]
    #subsystems = [dcc.Link(children=f.kind+" ", href=path+"/"+f.kind) for f in self.factories()]
    #subsystems = [html.Div(children=f.kind) for f in self.factories()]
    return html.Div(
        subsystems+
        ["Parameters"]+[info(self.__parameters__, "dash", depth-1)]
    )


