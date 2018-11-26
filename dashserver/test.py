from system.base import _loaddictwalk, _dumpdictwalk, info, pinfo, SystemProperty, Link ;
from vltsystem import vlt as vltsys; 
from vltsystem import parameters as p; 
from system import dashserver

import dash_core_components as dcc
import dash_html_components as html


import dash 

vlt = vltsys.Vlt(db=vltsys.db); 
l = Link("light")

app = dash.Dash()


#app.layout = vlt.vlti.dl1.__info__("dash")
app.layout = html.Div([
    dcc.Location(id='url', refresh=False), 
    html.Div(id="page-content")
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def appurl(url):
    url = url.strip("/")
    if not url or url=="/":
        s = vlt
    else:
        s = vlt.goto(url)
    print (url, s.__info__("dash"))
    return s.__info__("dash")

if __name__=="__main__":
    app.run_server(debug=True)