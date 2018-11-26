from utils.info import Info, reindent, info, pinfo, tablelize, tablelizehtml
import os
import builtins


def _parentKeysWalk(p, keys):
    if p is None:
        return
    keys.update(p.keys())
    return _parentKeysWalk(p.parent(), keys)


def _findFactory(s, kind):
    for k,v in s.__class__.__dict__.items():        
        if isinstance(v, Factory):
            if v.kind == kind:
                return v
        elif isinstance(v, SystemProperty):
            if v.factory:
                if v.factory.kind==kind:
                    return v.factory
            else:
                if v.kind==kind:
                    return Factory(kind=v.kind)


    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items(): 
            if isinstance(v, Factory):
                if v.kind == kind:
                    return v

            elif isinstance(v, SystemProperty):
                if v.factory:
                    if v.factory.kind==kind:
                        return v.factory
                else:
                    if v.kind==kind:
                        return Factory(kind=v.kind)



    return s.System or System

def _iterFactories(s):
    found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v, Factory):
            if v.kind not in found:
                yield v
                found.add(v.kind)

        elif isinstance(v, SystemProperty):
            if v.factory:
                if v.factory.kind not in found:
                    yield v.factory
                    found.add(v.factory.kind)

            else:                
                if v.kind not in found:
                    yield Factory(kind=v.kind)
                    found.add(v.kind)

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v, Factory):
                if v.kind not in found:
                    yield v
                    found.add(v.kind)

            elif isinstance(v, SystemProperty):
                if v.factory:
                    if v.factory.kind not in found:
                        yield v.factory
                        found.add(v.factory.kind)

                else:
                    if v.kind not in found:
                        yield Factory(kind=v.kind)
                        found.add(v.kind)

def _findDataSet(s, kind):
    for k,v in s.__class__.__dict__.items():        
        if isinstance(v, DataSet):
            if v.kind == kind:
                return v

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items(): 
            if isinstance(v, DataSet):
                if v.kind == kind:
                    return v                
    return None

def _iterDataSet(s):
    found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v, DataSet):
            if v.kind not in found:
                yield v
                found.add(v.kind)

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v, DataSet):
                if v.kind not in found:
                    yield v
                    found.add(v.kind)


def _findView(s, kind):
    for k,v in s.__class__.__dict__.items():        
        if isinstance(v, View):
            if v.kind == kind:
                return v

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items(): 
            if isinstance(v, View):
                if v.kind == kind:
                    return v                
    return None

def _iterView(s):
    found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v, View):
            if v.kind not in found:
                yield v
                found.add(v.kind)

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v, View):
                if v.kind not in found:
                    yield v
                    found.add(v.kind)


def _iterAction(s):
    #found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v, Action):
            yield v
           

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v, Action):
                yield v                

def _iterQuery(s):
    #found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v, Action):
            yield v
           
    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v, Action):
                yield v  

def _findPort(s, kind):    
    for k,v in s.__class__.__dict__.items():        
        if isinstance(v, Port):
            if v.kind == kind:
                return v

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items(): 
            if isinstance(v, Port):
                if v.kind == kind:
                    return v
    if kind is None:
        return None
    else:
        return _findPort(s, None)    


def _iterPort(s):
    found = set()
    for k,v in s.__class__.__dict__.items():
        if isinstance(v,Port):
            if v.kind not in found:
                yield v
                found.add(v.kind)

    for sub in s.__class__.__mro__:
        for k,v in sub.__dict__.items():
            if isinstance(v,Port):
                if v.kind not in found:
                    yield v
                    found.add(v.kind)


def _iterSystemsProperty(s, found, skind=None):

    if skind is None:
        for k,v in s.__class__.__dict__.items():
            if isinstance(v, SystemProperty):
                K = (v.id, v.factory.kind if v.factory else v.kind) 
                if not K in found:
                    found.add(K)
                    yield K
        
        for sub in s.__class__.__mro__:
            for k,v in sub.__dict__.items():
                if isinstance(v,SystemProperty):
                    K =(v.id, v.factory.kind if v.factory else v.kind)
                    if not K in found:
                        found.add(K)
                        yield K
    
    else:

        for k,v in s.__class__.__dict__.items():
            if isinstance(v, SystemProperty):
                if v.factory:
                    if v.factory.kind == skind:
                        K = (v.id, v.factory.kind)
                        if not K in found:                    
                            found.add(K)
                            yield K
                elif v.kind == skind:
                    K = (v.id, v.kind)
                    if not K in found:
                        found.add(K)
                        yield K

        for sub in s.__class__.__mro__:
            for k,v in sub.__dict__.items():
                if isinstance(v,SystemProperty):
                    if v.factory:
                        if v.factory.kind == skind:
                            K = (v.id, v.factory.kind)
                            if not K in found:
                                found.add(K)
                                yield (v.id, v.factory.kind)
                    elif v.kind == skind:
                        K = (v.id, v.kind)   
                        if not K in found:
                            found.add(K)
                            yield (v.id, v.kind)               


def _iterSystems(s, skind=None, addcashed=False):
    found = set()

    if skind is None:

        if addcashed:
            for (id,kind), sub in list(s.__subsystems__.items()):
                if id is DEFAULT: continue 
                if not (id,kind) in found:
                    yield (id,kind)
                    found.add((id,kind))
                
        for f in _iterFactories(s):
            kind = f.kind          
            try:
                iditerator = f.ids(s)
            except ValueError:
                continue
            else:
                for id in iditerator:
                    if id is DEFAULT: continue 
                    if not (id,kind) in found:
                        yield (id,kind)
                        found.add((id,kind))

        for s in _iterSystemsProperty(s, found):
            yield s


    else:

        if addcashed:
            for (id,kind), sub in list(s.__subsystems__.items()):
                if kind!=skind: continue
                if id is DEFAULT: continue 
                if not (id,kind) in found:
                    yield (id,kind)
                    found.add((id,kind))


        for f in _iterFactories(s):
            kind = f.kind
            if kind!=skind: continue
            try:
                iditerator = f.ids(s)
            except ValueError:
                continue
            else:
                for id in iditerator:
                    if id is DEFAULT: continue 
                    if not (id,kind) in found:
                        yield (id,kind)
                        found.add((id,kind))

        for s in _iterSystemsProperty(s, found, skind):
            yield s


def _dumpdictwalk(s,d):
    d['id'] = s.id
    d['kind'] = s.kind
    d['parameters'] = dict(s)

    childs = {}
    
    #for subs in _iterSystems(s, None, True):
    for subs in s.systems():
        if subs.master == s:            
            sd = {}
            childs[(subs.kind, subs.id)] = _dumpdictwalk(subs, sd)       
    
    d['childs'] = childs    
    return d


def _loaddictwalk(s, d):

    s.update(d['parameters'])
    for (kind, id), subd in d['childs'].items():
        _loaddictwalk(s.system(kind, id), subd) 
    


def _absolutepathwalk(s, path):
    p = s.parent()    
    if p:
        path.append((s.kind, s.id))
        _absolutepathwalk(p, path)



def incontext(context, v):
    try:
        c = v.__compute__
    except AttributeError:
        return v
    else:
        return c(context)

class SubSystemsView(object):
    def __init__(self, system, kind=None):
        self.system = system
        self.kind = kind

    def __iter__(self):
        for id,kind in _iterSystems(self.system, self.kind):
            yield self.system.system(kind=kind, id=id)

    def idkinds(self):
        return _iterSystems(self.system)

    def ids(self):
        for id,kind in _iterSystems(self.system, self.kind):
            yield id

    def kinds(self):
        for id,kind in _iterSystems(self.system, self.kind):
            yield kind


class FactoriesView(object):
    def __init__(self, system):
        self.system = system

    def __iter__(self):
        for f in _iterFactories(self.system):
            yield f

    def kinds(self):
        for f in _iterFactories(self.system):
            yield f.kind


class LinksView(object):
    def __init__(self, system, kind=None):
        self.links = system.__links__
        self.kind = kind
    
    def __iter__(self):
        if self.kind is None:
            for kind,d in self.links.items():
                for id,link in d.items():
                    yield link
        else:
            for lkind,d in self.links.items():
                if kind!=lkind: continue
                for id,link in d.items():
                    yield link

class IterIdError(ValueError):
    pass


class _DictMethods_:
    def keys(self):

        """ iterator on keys parameters """
        return self.__parameters__.keys()

    def items(self):
        """ iterator on key,value pairs of parameters """        
        for k in self.keys():
            yield k,self[k]

    def values(self):
        """ iterator on parameters values """
        for k in self.keys():
            yield self[k]

    def update(self, __d__={}, **kwargs):
        """ update parameters of system """
        for k,v in  dict(__d__, **kwargs).items():
            self[k] = v

    def setdefault(self, key, value):
        """ D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D """
        try:
            return self[key]
        except KeyError:
            self[key] = value
            return value

    def setdefaults(self, __d__={}, **kwargs):
        """ set several default keyword in one call 

        Args:
            d : key/value pairs dictionary 
            \*\*kwargs: Other key/values pairs dictionary 

        """   
        for k,v in dict(__d__, **kwargs).items():
            try:
                self[k]
            except KeyError:
                self[k] = v    

    def get(self, key, default=None):
        """ return parameter value of given key or default """
        try:
            return self[key]
        except KeyError:
            return default

    def gets(self, *args, **kwargs):
        """ return several parameters in one call

        takes several string argument which correspond to parameters name
        and return the same number of values.
        Defaults can be set by keyword argument of the same parameter name

        temp, speed, x, y = o.gets("temp", "speed", "x", "y", x=0.0, y=0.0)
        
        """
        for a in args:
            try:
                v = self[a]
            except KeyError:
                try:
                    v = kwargs[a]
                except KeyError:
                    raise KeyError('%r'%a)            
            yield v

    def __getitem__(self, key):
        return self.__parameters__[key]

    def __setitem__(self, key, value):
        self.__parameters__[key] = value


DEFAULT = "__DEFAULT__"

class System(_DictMethods_):
    """ Base System object """
    Locals = dict
    Globals = dict
    Privates = dict

    System = None
    Factory = None
    
    _parent = None
    _master = None
    _kind = None
    _id = None
    _db = None

    def __init__(self, parent=None, id=None, kind=None, db=None, master=None, mode=None, **parameters):
        """ create a new system instance 

        All arguments are optionals, all except the ones described below are local parameters of
        the created system.

        Args:
            parent (:class:`System`,optional):  The parent system, system for which the new instance
                is supposed to be located.
            id (hashable, optional): Id of the new system created. 
                if id is new, the system instance will re
            kind (hashable, optional): kind of the new system created
                If defined overwrite the one defined in the class definition
                kind must be preferable a comprehensive string like 'motor', 'cabinet', 'sensor' etc..
            db (any, optional): The database used to create a new sub-system from the sub-system factory
                db is parsed from sub-system to system usually one only needs to set it in the root 
                system
            master (:class:`System`, optional):  master :class:`System` 
                all the system parameters will be stored inside the master. Meaning that systems
                with the same id, kind and master is the saem object.
                If not given, master is parent. See :mod:`system` doc to understand the difference 
                between 'master' and 'parent'
            \*\*parameters : all other parameters available as item : system['param1'] 
        
        Returns:
            :class:`System`
        
        """    
        if parent is not None:
            self._parent = parent
        if master is not None:
            self._master = master
        elif self._master is None:
            self._master = self._parent

        if kind is not None:
            self._kind = kind
        if id is not None:
            self._id = id
        if db is not None:
            self._db = db

        self.__rebuild__()
        self.update(**parameters)

    def __getitem__(self, key):
        try:
            v = self.__parameters__[key]
        except KeyError:
            pass
        else:
            return incontext(self, v)

        parent = self
        while parent:
            try:
                v = parent.__globals__[key]               
            except KeyError:
                pass
            else:
                return incontext(parent, v)
            parent = parent.parent()

        raise KeyError("%r"%key)

    def __get__(self, parent, cls=None):
        if parent is None:
            return self
        return self.Factory(parent=parent, id=self.id)
    

    def __eq__(self, right):
        # two systems are equal if they share the same parameters
        try:
            rp = right.__parameters__
        except AttributeError:
            return False
        return self.__parameters__ is right.__parameters__

    @property
    def id(self):
        """ system id """
        return self._id

    @id.setter
    def id(self, id):
        self._id = id
        self.__rebuild__()

    @property
    def kind(self):
        """ system kind """
        return self._kind

    @kind.setter
    def kind(self, kind):
        self._kind = kind
        self.__rebuild__()
    
    def setMode(self,mode):
        self.__privates__["mode"] = mode

    def getMode(self):
        mode = self.__privates__.get("mode", None)
        if mode is None: 
            if self._parent:
                return self._parent.getMode()
            else:
                return None        
        return mode 


    def parent(self, kind=None):
        """ return the parent of the system or None 

        Without argument the first parent is returned
        with kind as argument, the first parent of that the kind is returned.
        *Note* that if the current system match the kind, it will returned.
        This allow to make quick query like `s.parent("sensor")['status']`
        
        If parent is not found, None is returned.
        
        Args:
            kind (hashabl, optional): If None (default) return the parent
                if given return the firs occurrence of parent of that kind
                
        Returns:
            :class:`System` or None if no parent exists 

        Example:
            
            >>> lab = System(kind="lab", id=0)
            >>> cabinet = System(lab, kind="cabinet", id=0)
            >>> sensor = System(cabinet, kind="sensor", id=56)

            >>> environment = sensor.parent("cabinet") or sensor.parent("laboratory")
            
            >>> sensor.parent("sensor") == sensor
            True
        
        """
        if kind is None:
            return self._parent

        if self.kind == kind:
            return self
        if self._parent is None:
            return None
        return self._parent.parent(kind)        

    @property
    def master(self):
        return self._master

    @property
    def db(self):
        """ system shared data base (can be anything)"""
        if self._db is None:
            return self.parent().db
        return self._db

    def __rebuild__(self):
        """ rebuild the system 

        load the defined, parameters, globals, subsystems and links which should be inside the master.
        If no master, define the parameters in self.
        """

        if self._id is None:
            p = getattr(self, "__parameters__", {})
            self.__parameters__ = self.Locals()
            self.__globals__    = self.Globals()
            self.__privates__   = {}
            self.__subsystems__ = {}
            self.__links__ = {}
            self.update(p)


        elif self._id is DEFAULT:
            if self._master is None:
                self.__parameters__ = self.Locals()
                self.__globals__    = self.Globals()
                self.__privates__   = {}
                self.__subsystems__ = {}
                self.__links__ = {}
                    
            else:
                try:
                    parameters, gbls, subsystems, links, privates = self._master.__subsystems__[(DEFAULT, self._kind)]
                except KeyError:
                    parameters = self.Locals()
                    gbls = self.Globals()
                    prvs = {}
                    subsystems = {}
                    links = {}
                    self._master.__subsystems__[(DEFAULT, self._kind)] = (parameters, gbls, subsystems, links, prvs)
                    self.__parameters__, self.__globals__, self.__subsystems__, self.__links__, self.__privates__ = parameters, gbls, subsystems, links, prvs
                    
                else:
                    self.__parameters__, self.__globals__, self.__subsystems__, self.__links__, self.__privates__ = parameters, gbls, subsystems, links, prvs

        else:
            if self._master:

                try:
                    defaults, defaultgbls, _, _, _ = self._master.__subsystems__[(DEFAULT, self._kind)]
                except KeyError:
                    defaults = {}
                    defaultgbls = {}
                    privates = {}
                try:
                    parameters, gbls, subsystems, links, privates = self._master.__subsystems__[(self._id, self._kind)]
                except KeyError:
                    parameters = self.Locals()
                    gbls = self.Globals()
                    privates = {}

                    subsystems = {}
                    links = {}
                    for k in defaults:                           
                        parameters[k] = defaults[k]

                    self._master.__subsystems__[(self._id, self._kind)] = (parameters, gbls, subsystems, links,privates)
                    (   self.__parameters__,  self.__globals__, 
                        self.__subsystems__, self.__links__, self.__privates__
                    ) = (                    
                        parameters, gbls, subsystems, links,privates
                    )

                else:
                    self.__parameters__, self.__globals__, self.__subsystems__, self.__links__, self.__privates__ = parameters, gbls, subsystems, links, privates
            else:
                self.__parameters__ = self.Locals()
                self.__globals__ = self.Globals()
                self.__privates__   = {}
                self.__subsystems__ = {}
                self.__links__ = {}
        
        if self._id is not None and self._kind is not None:
            self.__globals__.setdefault(self._kind, self._id)

    def getAbsolutePath(self):
        path = []
        _absolutepathwalk(self, path)
        return "/".join("%s/%s"%(k,i) for k, i in reversed(path))

    def goto(self, spath):
        path = spath.split("/")
        f = None
        s = self
        for p in path:
            if f:
                try: 
                    p = int(p)
                except (ValueError, TypeError):
                    try:
                        p = float(p)
                    except (ValueError, TypeError):
                        pass            
                s = f(p)
                f = None
            else:
                f = s.factory(p)
        if f:
            return f
        return s


    def links(self, kind=None):
        """ iterable object of all the links receive by the system 

        if a link kind is given the iterable is limited to the link of that kind.

        Args:
            kind (hashable, None, optional): reduce the iterable to the one that match this kind.

        Returns:
            :class:`LinksView`

        See Also:
            methods: :meth:`link`, :meth:`recieve`, :meth:`send`, :meth:`propagate` 
            objects: :class:`Link`            
        """
        return LinksView(self, kind=kind)

    def _storeLink(self, link):
        kd = self.__links__.setdefault(link.kind, {})
        id = link.id if link.id is not None else len(kd)
        kd[id] = link
    

    def link(self, kind, id=None):
        """ return the link of given kind and id 
        
        if id is not given return the unique link of that kind, 
        if they are several link matching the kind raise a ValueError

        Args:
            kind (hashable):  link kind to find  
            id (hashable, optional): link id 
        """
        try:
            d = self.__links__[kind]
        except KeyError:
            raise ValueError("link of kind=%r does not exists"%(kind))     

        if id is None:
            if len(d)>1:
                raise ValueError("They are several link with kind %r, provide an id"%kind)
            else:
                return d[list(d.keys())[0]]

        try:
            return d[id]
        except KeyError:
            raise ValueError("link of kind=%r and id=%r does not exists"%(kind,id))    

    def allkeys(self):
        """ returned a iterable on all the keys, including the parent global keys 

        system object can have locals and globals keys. The globals keys are passed
        from the parent to the childs and can be acceded from the child.
        ::
            >>> s.allkeys()
            is equivalent to:
            >>> s.all.keys()

        See Also:
            :prop:`all`, :prop:`locals`, :prop:`globals`

        """
        found = set()

        for k in self.__parameters__.keys():            
            yield k
            found.add(k)
        
        parent = self
        while parent:
            for k in parent.__globals__.keys():
                if k not in found:
                    yield k
                    found.add(k)
            parent = parent.parent()
    

    def port(self, lkind):
        port = _findPort(self, lkind)
        return port.__get__(self, None)


    def receive(self, link_or_path, *ways):
        """ receive a link 

        the link can be a :class:`Link` object or a string kind. If a kind Link instance
        is made on the fly: `Link(link)
        
        """
        if isinstance(link_or_path, str):
            link_or_path = Link(link_or_path)

        if isinstance(link_or_path, Path):
            lkind = link_or_path.link.kind
        else:
            lkind = link_or_path.kind

        port = _findPort(self, lkind)

        if port is None:            
            return []

        port = port.__get__(self, None)
        return port.receive(link_or_path, *ways)
    
    def send(self, link_kind):
        port = _findPort(self, link_kind)
        if port is None:
            return None

        port = port.__get__(self, None)
        return port.send(link_kind)
       
    
    def propagate(self, link):
        port = _findPort(self, link.kind)
        if port is None:
            return None
        port = port.__get__(self, None)
        return port.propagate(link)

    def system(self, kind=None, id=None, db=None, **parameters):            
        Factory = self.factory(kind)
        return Factory(parent=self, id=id, kind=kind, db=db, **parameters)

    def systems(self, kind=None):
        return SubSystemsView(self, kind)

    def factory(self, kind):
        if kind is None:
            return self.System or System
        f = _findFactory(self, kind)
        return FactoryInstance(f, self)

    def factories(self):
        return FactoriesView(self)

    def created(self, id, kind):
        return (id, kind) in self.__subsystems__


    def dump(self):
        d = {}
        _dumpdictwalk(self,d)
        return d

    def load(self, d):
        if not all(k in d for k in ["id", "kind", "parameters", "childs"]):
            raise ValueError("Dictionary dos not seems to be compatible keys 'id', 'kind', 'parameters', 'childs' are needed")

        if self.kind != d['kind']:
            raise ValueError("cannot load dictionary system is of kind %r while the dictionary start with %r"%(self.kind, d['kind']))

        if self.id is not None and self.id!=d['id']:
            raise ValueError("cannot load dictionary system of id %r while the dictionary start with id %r"%(self.id, d['id']))
        _loaddictwalk(self, d)
        
    

    @property
    def locals(self):
        return LocalsView(self)

    @property
    def all(self):
        return AllView(self)
    
    @property
    def globals(self):
        return GlobalsView(self)
    
    def __repr__(self):
        return "<%s.%s at 0x%0x kind=%r id=%r>"%(
                 globals()['__name__'],
                 self.__class__.__name__, 
                 id(self), 
                 self.kind, 
                 self.id                 
                )

    @Info
    def __info__(self, depth):
        return info(self, "ascii")

    @__info__.case("ascii")
    def __info__(self, depth):
        if depth == 0:
            return repr(self)

        text = "{mod}.{cl} id={id} kind={kind}\n".format(
            mod =globals()['__name__'],
            cl  =self.__class__.__name__,
            kind=info(self.kind, "ascii", depth), 
            id  =info(self.id,   "ascii", depth)            
        )
        text += "-"*(len(text)-1)+"\n"
        text += "Parameters:\n"
        text += reindent(info(self.__parameters__, "ascii",depth))
        text += "\n\n"
        #text += "Other Parameters (from parents):\n"
        #pks = set()
        #_parentKeysWalk(self.parent(), pks)       
        #text += reindent(tablelize("%r"%s for s in pks))

        #text += "\n\nPath: %s"%info(self.path, "ascii", depth)

        #if self.parent:
        #    text += "\n"+reindent(info(self.parent, "ascii",depth))
        return text
    
    @__info__.case("html")
    def __info__(self, depth):
        if depth == 0:
            return repr(self)

        txt = """<ul class='System'>
                 <li class='System-classname'>System: {mod}.{cl}</li>
                 <li class='System-id'>id: {id}</li>
                 <li class='System-kind'>kind: {kind}</li>                                
            """.format(
                mod =globals()['__name__'],
            cl  =self.__class__.__name__,
            kind=info(self.kind, "html", depth), 
            id  =info(self.id,   "html", depth)            
        )
        txt += "<li class='Parameters-title'>Parameters</li>"
        txt += "<ul class='System-parameters'>"
        txt += info(self.__parameters__, "html", depth)
        txt += "</ul>"

        txt += "<li class='Parameters-title'>Parent</li>"
        txt += "<div class='System-parent'>"
        txt += info(self.parent(), "html", depth)      
        txt += "</div>"
        txt += "</ul>"        
        return txt

    def _repr_html_(self):
        """ for ipython notebook qtconsole etc ... """
        return info(self, "html")


class Action(object):
    def __init__(self, func):
        self.__func__ = func
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls=None):
        if obj is None:
            return obj
        return ActionInstance(self, obj)

class ActionInstance(object):
    def __init__(self, action, system):
        self.action = action 
        self.system = system
        self.__doc__ = self.action.__doc__

    def __call__(self, *args, **kwargs):
        return self.action.__func__(self.system, *args, **kwargs)
action = Action

class Query(object):
    def __init__(self, func):
        self.__funcs__ = {None:func}
        self.__doc__ = func.__doc__

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return QueryInstance(self, obj)

    def setMode(self, mode, func):
        if mode in ["mode","setMode"]:
            raise ValueError("mode cannot be on of 'mode', 'setMode',got %r"%mode)
        self.__funcs__[mode] = func

    def mode(self, mode):
        def modeSetter(func):
            self.setMode(mode,func)
            return self
        return modeSetter

class QueryInstance(object):
    def __init__(self, query, system):
        self.query = query 
        self.system = system
        self.__doc__ = self.query.__doc__

    def __call__(self, *args, **kwargs):
        mode = self.system.getMode()
        try:
            f = self.query.__funcs__[mode]
        except KeyError:
            try:
                f = getattr(self.query, mode)
            except AttributeError:
                raise ValueError("Cannot find query function for current mode %r"%mode)

        return f(self.system, *args, **kwargs)
        #return self.query.__func__(self.system, *args, **kwargs)        
query = Query     


class Port(_DictMethods_):
    Parameters = dict    
    _kind = None
    
    def __init__(self,  kind=None, **parameters):        
        if kind is not None:
            self._kind = kind

        self.__parameters__  = self.Parameters()
        self.update(parameters)

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return PortInstance(self, obj)

    def receive(self, system, link, then=None):
        if False:
            yield link
    
    def receiver(self, func):
        self.receive = func
        return self

    @property
    def kind(self):
        return self._kind


def _it2s(it):
    if it is None:
        return None
    if isinstance(it, System):
        return it
    else:
        s = None
        for i,s in enumerate(it):
            if i:
                raise ValueError("system %r yield several system expecting one")
        if s is None:
            return None
        return s

def _propagate_walk(receive, path, ways):
    
    if not len(ways):
        it = receive(path.system, path)
        s = _it2s(it)
        return path
        #newPath = Path(list(path._pairs), len(path._pairs)-1)
        #newPath.newSystem(s)
        #return newPath

    it = receive(path.system, path, ways[0])
    s = _it2s(it)

    if s is None:
        return None
        
    p = _findPort(s, path.link.kind)
    if p is None:
        return path.writeHistory("trying to send link %r to system %r but no port for %r was found"%(
                                path.link.kind, (s.kind,s.id), path.link.kind
                                )
                )
    if s == ways[0]:        
        ways = ways[1:]

    newPath = Path(list(path._pairs), len(path._pairs)-1)
    newPath.newSystem(s)

    return _propagate_walk(p.receive, newPath, ways)


def _receive_walk(receive, path):
    it = receive(path.system, path)   
    if it is None or it is False:
        return [path]
    if isinstance(it, System):
        it = [it]

    branches = [] 
    one = False   
    for s in it:
        one = True     
        p = _findPort(s, path.link.kind)   
        if p is None:
            path.writeHistory("trying to send link %r to system %r but no port for %r was found"%(
                                path.link.kind, (s.kind,s.id), path.link.kind
                                )
                )
            continue
        newpath = Path( list(path._pairs), len(path._pairs)-1)
        newpath.newSystem(s)

        branches.extend(_receive_walk(p.receive, newpath))

    if not one:
        return [path]

    return branches




class PortInstance(object):
    def __init__(self, port, system):
        self.port = port
        self.system = system

    def receive(self, link_or_path, *ways):
        if isinstance(link_or_path, Path):
            path = link_or_path
            path.newSystem(self.system)

        elif isinstance(link_or_path, Link):
            path = Path([(link_or_path, self.system)])
        else:
            raise ValueError("expecting a Link or a Path object got a %r"%type(link_or_path))

        if ways:
            return _propagate_walk(self.port.receive, path, ways)        

        else:
            return _receive_walk(self.port.receive, path)

    def __call__(self, link):
        return self.receive(link)


def port(kind, **parameters):
    newport = Port(kind,**parameters)
    return newport.receiver


class GlobalsView(_DictMethods_):
    def __init__(self, obj):
        object.__setattr__(self, "__obj__",  obj)

    def keys(self):
        return self.__obj__.__globals__.keys()

    def __getitem__(self, key):
        v = self.__obj__.__globals__[key]
        return incontext(self.__obj__, v)

    def __setitem__(self, key, value):
        self.__obj__.__globals__[key] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%r"%attr)

    def __iter__(self):
        return self.keys().__iter__()

    def __setattr__(self, attr, value):
        self[attr] = value


class AllView(_DictMethods_):
    def __init__(self, obj):
        object.__setattr__(self, "__obj__",  obj)

    def keys(self):
        found = set()
        
        for k in self.__obj__.__parameters__.keys():            
            yield k
            found.add(k)
        
        parent = self.__obj__
        while parent:
            for k in parent.__globals__.keys():
                if k not in found:
                    yield k
                    found.add(k)
            parent = parent.parent()


    def __getitem__(self, key):        
        return self.__obj__[key]


    def __setitem__(self, key, value):
        self.__obj__[key] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%r"%attr)

    def __iter__(self):
        return self.keys().__iter__()

    def __setattr__(self, attr, value):
        self[attr] = value



class LocalsView(_DictMethods_):
    def __init__(self, obj):
        object.__setattr__(self, "__obj__",  obj)

    def keys(self):
        return self.__obj__.keys()

    def __getitem__(self, key):
        return self.__obj__[key]

    def __setitem__(self, key, value):
        self.__obj__[key] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%r"%attr)

    def __iter__(self):
        return self.keys().__iter__()

    def __setattr__(self, attr, value):
        self[attr] = value



class RecParamsView(_DictMethods_):
    def __init__(self, obj):
        object.__setattr__(self, "__obj__",  obj)

    def keys(self):
        s = self.__obj__
        found = set()
        while s:
            for k in s.keys():
                if not k in found:
                    yield k
                    found.add(k)
            s = s.parent()
    
    def __setitem__(self, key, value):
        raise KeyError("Recursive view of params is read only")

    def __getitem__(self, key):        
        s = self.__obj__
        while s:    
            try:
                return self.__obj__[key]
            except KeyError:
                pass
            s = s.parent()
        raise KeyError("%r"%key)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError("%r"%attr)

    def __setattr__(self, attr, value):
        self[attr] = value


class Link(_DictMethods_):
    Parameters = dict    
    _kind = None    
    _id = None    

    def __init__(self, kind=None, id=None, history=None, **parameters):        
        if kind is not None:
            self._kind = kind
        if id is not None:
            self._id = id

        self.__parameters__ = self.Parameters()
        self.update(parameters)                
        self._history = [] if history is None else list(history)


    def __getitem__(self, key):
        v = self.__parameters__[key]
        return incontext(self, v)

    def __repr__(self):
        return "<%s.%s at 0x%0x kind=%r id=%r >"%(
                globals()['__name__'],
                 self.__class__.__name__, 
                 id(self),
                 self.kind,
                 self.id
            )
    
        
    def copy(self):
        return self.__class__(kind=self.kind, id=self.id,                               
                              #history= self._history,
                               **self
                            )
    @property
    def kind(self):
        return self._kind 

    @property
    def id(self):
        return self._id
       
    @property
    def history(self):
        # to be consistant with path return a copy of the history 
        return list(self._history)

    def writeHistory(self, msg):
        self._history.append(msg)



class Path(object):

    def __init__(self, pairs, current=0):
        self._pairs = pairs
        self._current = current
    
    def __getitem__(self, pos):
        if isinstance(pos, slice):
            return Path( self._pairs[pos] )

        return Path( self._pairs, pos)

    #def __getitem__(self, key):
    #    v = self.__parameters__[key]
    #    return incontext(self._pairs[self._current][0], v)

    def __repr__(self):
        return "<%s.%s at 0x%0x link=%r  system=%r  step=%d/%d>"%(
                globals()['__name__'],
                 self.__class__.__name__, 
                 id(self), 
                 (self.link.kind,self.link.id), 
                 (self.system.kind,self.system.id),  
                 self._current,
                 len(self._pairs)-1
                 )

    @property
    def __parameters__(self):
        return self._pairs[self._current][0].__parameters__
    
    @property
    def link(self):
        return self._pairs[self._current][0]

    @property
    def system(self):
        return self._pairs[self._current][1]

    def previousSystem(self, kind=None):
        if kind is None:
            if self._current<=0:
                return None
            return self._pairs[self._current-1][1]

        for l,s in reversed(self._pairs):
            if s.kind == kind:
                return s
        return None

    def previousLink(self, kind=None):
        if kind is None:
            if self._current<=0:
                return None
            return self._pairs[self._current-1][0]

        for l,s in reversed(self._pairs):
            if s.kind == kind:
                return l
        return None

    def previousState(self, kind=None):
        if kind is None:
            if self._current<=0:
                return None
            return Path(
                    self._pairs, 
                    self._current-1
                )

        for i,(l,s) in enumerate(reversed((self._pairs))):
            if s.kind == kind:
                return Path(
                    self._pairs, 
                    len(self._pairs)-i-1
                )
        return None

    def writeHistory(self, msg):
        #print(msg)
        self.link._history.append(str(msg))

    @property    
    def history(self):
        return sum( (self._pairs[i][0]._history for i in\
                    (range(0,self._current+1))), []                   
                )
    
    def previous(self):        
        if self._current<=0:
            raise StopIteration()

        return Path(
                self._pairs, self._current-1
            )

    def next(self):
        if self._current>=len(self._links):
            raise StopIteration()

        return Path(
                self._pairs, self._current-1
            )

    def fwd(self):
        self._current = len(self._links)-1        

    def rwd(self):
        self._current = 0        

    def add(self, pair):
        pair = tuple(pair)
        if len(pair)!=2:
            raise ValueError("expecting a 2 tuple as argument got %r"%pair)
        self._pairs.append(pair)
        self._current = len(self._pairs)-1

    def newSystem(self, s):
        self.add( (self._pairs[-1][0].copy(),s))




class Factory(_DictMethods_):
    __ids__  = None
    __make__ = None
    __id__   = None

    System = System    
    Parameters = dict
    _kind = None
    _db = None
    _path = None
    def __init__(self, System=None, kind=None, db=None, path=None, 
                        id=None, ids=None, master=None, make=None, 
                        parent=None, **parameters):
        if System is not None:
            self.System = System

        if kind is not None:
            self._kind = kind
        
        if self._kind is None:
            self._kind = self.System._kind

        if db is not None:
            self._db = db

        if path is not None:
            self._path = path

        if id is not None:
            if not hasattr(id, "__call__"):
                raise ValueError("expecting a callable function for id got %r"%id)
            self.__id__ = id

        if ids is not None:
            if not hasattr(ids, "__call__"):
                raise ValueError("expecting a callable function for ids got %r"%ids)
            self.__ids__ = ids

        if make is not None:
            if not hasattr(make, "__call__"):
                raise ValueError("expecting a callable function for make got %r"%make)
            self.__make__ = make

        if master is not None:
            if not hasattr(master, "__call__"):
                raise ValueError("expecting a callable function for master got %r"%master)
            self.__master__ = master

        if parent is not None:
            if not hasattr(parent, "__call__"):
                raise ValueError("expecting a callable function for parent got %r"%parent)
            self.__parent__ = parent


        self.__parameters__ = self.Parameters()
        self.update(parameters)


    def __call__(self, parent=None, id=None, kind=None, db=None, **parameters):        
        kind = self.kind if kind is None else kind        
        db = self.db if db is None else db

        parent = self.__parent__(parent)
        master = self.__master__(parent)

        if self.path:
            if not parent:
                raise ValueError("path exists but no parent")
            
            for k,i in self.path:            
                parent = parent.system(id=i,kind=k)            

        if id is None:
            id = self.id(parent)


        exists = master and master.created(id,kind)

        if not exists:
            parameters = dict(self.__parameters__, **parameters)        
        new = self.System(parent=parent, id=id, kind=kind, db=db, master=master, **parameters)

        if not exists:
            self.make(new)
        return new

    def __call__(self, parent=None, definition=None, id=None, kind=None, db=None, **parameters):        
        kind = self.kind if kind is None else kind        
        db = self.db if db is None else db

        parent = self.__parent__(parent)
        master = self.__master__(parent)

        if definition is not None:

            if hasattr(definition, "keys"):
                definition = dict(definition)
                try:
                    did = definition['id']
                except:
                    if id is None:
                        id = builtins.id(definition) # :TODO: need to make a truly unique id
                else:
                    if id is None:
                        id= did
                    elif id!=did:
                        raise ValueError("id in dictionary definition %r is not the same then id in keyword argument %r"%(did, id))

                kind = kind if kind is not None else definition.get("kind", None)
            
                exists = master and master.created(id,kind)
                if not exists:
                    parameters = dict(self.__parameters__, **parameters)
                parameters = dict(definition, **parameters)
                parameters.pop("id", None)
                parameters.pop("kind", None)
                new = self.System(parent=parent, id=id, kind=kind, db=db, master=master, **parameters)
                return new
            else:
                if id is None:
                    id = definition
                elif id!=definition:
                    raise ValueError("if definiton is an id, id keyword argument can't be given")


        if self.path:
            if not parent:
                raise ValueError("path exists but no parent")
            
            for k,i in self.path:            
                parent = parent.system(id=i,kind=k)            

        if id is None:
            id = self.id(parent)


        exists = master and master.created(id,kind)

        if not exists:
            parameters = dict(self.__parameters__, **parameters)        
        new = self.System(parent=parent, id=id, kind=kind, db=db, master=master, **parameters)

        if not exists:
            self.make(new)
        return new



    def __get__(self, parent, cls=None):
        if parent is None:
            return self
        return FactoryInstance(self, parent)

    def __parent__(self, parent):
        return parent

    def __master__(self, parent):
        return parent
    
    @property
    def kind(self):
        return self._kind

    @property
    def db(self):
        return self._db

    @property
    def path(self):
        return self._path

    def maker(self, func):
        if not hasattr(func, "__call__"):
            raise ValueError("expecting a callable object")
        self.__make__ = func
        return self

    def iditerator(self, func):
        if not hasattr(func, "__call__"):
            raise ValueError("expecting a callable object")
        self.__ids__ = func
        return self

    def ids(self, parent):
        if self.__ids__:
            return self.__ids__(parent)
        raise IterIdError("This Factory has no id iterator")    

    def id(self, parent):
        if self.__id__:
            return self.__id__(parent)
        raise IterIdError("This Factory has no default id generator")  
    


    def make(self, s):
        if self.__make__:
            self.__make__(s)
        

class FactoryInstance(object):
    def __init__(self, factory,  parent):
        self.factory = factory
        self.parent = parent

    def __call__(self, id=None, kind=None, **parameters):
        return self.factory(parent=self.parent, id=id, kind=kind, **parameters)

    def __call__(self, definition=None, id=None, kind=None, **parameters):
        return self.factory(parent=self.parent, definition=definition,
                            id=id, kind=kind, **parameters)

    def __getitem__(self, id):
        return self.factory(parent=self.parent, id=id)

    def ids(self):
        return self.factory.ids(self.parent)
    
    def __iter__(self):
        for id in self.ids():
            yield self(id=id)

    def __repr__(self):
        return "<FactoryInstance at 0x%0x factory=%s() parent=%s/%s>"%(
                id(self), 
                self.factory.__class__.__name__,
                self.parent.kind, 
                self.parent.id
            )

class SystemProperty(object):
    def __init__(self, kind_or_factory, id=None):
        if isinstance(kind_or_factory, Factory):
            self.factory = kind_or_factory
            self.kind = None
        else:
            self.factory = None
            self.kind = kind_or_factory
        self.id = id

    def __get__(self, obj, cls=None):
        if obj is None:
            return self

        if self.factory:
            return self.factory.__get__(obj, None)(id=self.id)
        else:
            return obj.system(kind=self.kind, id=self.id)



class View(object):
    _kind = None
    def __init__(self, name, kind=None, func=None, **parameters):
        if kind is not None:
            self._kind = kind
        if func is not None:
            self._func = func
        self.name = name

    def __get__(self, obj, cl=None):
        if obj is None:
            return self 
        return ViewInstance(self, obj)

class ViewInstance(object):    
    def __init__(self, view, obj):
        self.view = view
        self.obj = obj

    def __call__(self, **kwargs):
        return self.view._func(self.obj, **kwargs)

def view(name, kind=None):
    v = View(name, kind=kind)
    def setviewfunc(f):
        v._func = f
        return v
    return setviewfunc

############################################
#
#  laboratory to be cleaned !
#
############################################


class DataSet(object):
    _kind = None
    description = ""
    name = ""
    dtype = None
    def __init__(self, kind=None, name=None, dtype=None, description=None, fget=None, fiter=None, frender=None, **kwargs):
        if kind is not None:
            self.kind = kind
        if description is not None:
            self.description = description
        if name is not None:
            self.name = name
        if dtype is not None:
            self.dtype = dtype
        if fget is not None:
            self.fget = fget
        if fiter is not None:
            self.fiter = fiter

        self.__dict__.update(kwargs)

    def __get__(self, system, cls=None):
        if system is None:
            return self
        return DataSetInstance(self,system)

    @property
    def getter(self):
        def _fgetsetter(func):
            self.fget = func
            return self
        return _fgetsetter

    @property
    def iterator(self):
        def _fitersetter(func):
            self.fiter = func
            return self
        return _fitersetter

    @property
    def renderer(self):
        def _rendersetter(func):
            self.frender = func
            return self
        return _rendersetter
        
    def fget(self):
        raise NotImplementedError("fget not implemented")

    def fiter(self):
        raise NotImplementedError("fiter not implemented")

    def frender(self, data, context):
        return data

    def get(self, system, *args, **kwargs):
        return self.fget(system, *args, **kwargs)
        context = kwargs.pop("context", None)
        return self.frender(self.fget(system, *args, **kwargs), context)

    @classmethod
    def from_decorator(cl, kind=None, name=None, dtype=None, description=None, fget=None, fiter=None):
        new = cl(kind=kind, name=name, dtype=dtype, description=description, fget=fget, fiter=fiter)
        def _decorate_data(func):
            return new.getter(func)
        return _decorate_data

dataset = DataSet.from_decorator

class DataSetInstance(object):
    def __init__(self, dataset, system):
        self.dataset = dataset
        self.system = system

    def __call__(self, *args, **kwargs):
        return self.dataset.get(self.system , *args, **kwargs)   

    def __len__(self):
        return len(list(self.dataset.fiter(self.system)))

    def __iter__(self):
        for name, kwargs in self.dataset.fiter(self.system):
            yield self.dataset.get(self.system, **kwargs)

class Data(object):
    def __init__(self,header,data):
        self.header = header
        self.data = data
    @Info
    def __info__(self,depth):
        return repr(self)

class Document(Data):

    @Data.__info__.case("html")
    def __info__(self, depth):
        return """<span class=System_document style='background-color:#998899'>{description}<a href='file://{path}'>{filename}</a></span>""".format(
                description = self.header.get("description", ""), 
                filename = os.path.split(self.data)[1], 
                path = self.data
            )    
    def _repr_html_(self):
        return info(self, "html")

    def _repr_png_(self):
        return open(self.data, "r").read()


class Documents(DataSet):
    def __init__(self,*args, **kwargs):
        DataSet.__init__(self, *args, **kwargs)
        if not hasattr(self, "directory"):
            raise ValueError("missing mendatory 'directory' property")
    def fget(self, system, file=""):
        return Document({"path":file}, os.path.join(self.directory, file))

    def frender(self, path, context):
        if context == "html":
            return "<a href='file://%s'>%s</a>"%(path, path)
        return path

    def fiter(self, system):
        pass


def issystem(obj, kind=None):
    """ return True if the object is a system else False

    if kind arg is given and the object is not a system of that kind 
    a ValueError is raise.
    """
    if not isinstance(obj, System):
        return False
    if kind is None:
        return True
    if isinstance(kind, (tuple,list)):
        if not obj.kind in kind:
            raise ValueError("Expecting a System of kind '%s' got a %r"%("' or '".join(kind), obj.kind))
    elif obj.kind != kind:
        raise ValueError("Expecting a System of kind %r got a %r"%(kind, obj.kind))
    return True


