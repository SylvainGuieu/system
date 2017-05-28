from collections import OrderedDict
from values import Value, Compute
import re
Path = OrderedDict
Parameters = OrderedDict
Db = OrderedDict
Childs = dict

try:
    unicode
except NameError: 
    basestring = (str,bytes) # python3
ANONYMOUS = "anonymous"

def _todict_walker(d, childs):
    for (name,id),(parameters, subchilds) in childs.items():
        d[(name,id)] = dict(parameters)
        _todict_walker(d[(name,id)], subchilds)


_sysspliter = re.compile("([/]*)([^/]*)")
def goto(obj, s):
    first = True
    for i,subs in enumerate(_sysspliter.findall(s)):
        slashes, path = subs

        if not i and len(slashes)==1:
            # get the root system 
            while True:
                try:
                    obj = obj.parent()
                except StopIteration:
                    break            

        if len(slashes)>1:
            # get the parent followed after the two slashes
            name, p, _ = path.partition(":")
            if p:
                raise ValueError("at %r, id is given while parent is needed"%(slashes+path))
            obj = obj.parent(path)
            continue

        if not path:
            continue

        if path == ".":
            continue
        if path == "..":
            try:
                obj = obj.parent()
            except StopIteration:
                pass
            continue

        name, p, sid = path.partition(":")   
        if not sid:
            id = None
        else:
            try:
                id = int(sid)
            except ValueError:
                try:
                    id = float(sid)
                except ValueError:
                    id = sid
        obj = obj.child(name, id)

    return obj


class SystemPattern(type):
    def __new__(thiscls, name=None, Parameters=None, cls=None, clsName=None, **kwargs):
        cls = cls or System
        d = {}


        if name is not None:
            d['name'] = name

        if Parameters is not None:
            d['Parameters'] = Parameters
            d['parameters'] = Parameters()
        else:
            d['parameters'] = cls.Parameters()

        d['parameters'].update(kwargs)

        if clsName is None:
            clsName = cls.__name__+(name.capitalize() if name is not None else "%d"%id(thiscls))
        return type.__new__(thiscls, clsName, (cls,), d)

    def __init__(self, *args, **kwargs):
        pass # everything done in __new__

class System(object):
    Parameters = Parameters
    parameters = Parameters()
    name = ANONYMOUS

    def __init__(self, parent=None, name=None, id=None, db=None,  **kwargs):
        """ return a new System object 

        Parameters
        ----------
        parent: System, optional 
                The parent system for which the System is created
        name : string, optional
               the system name. if None take the class default
        id : any hashable, optional   
            a unique id for this system of that name. if present 
            the parent will record the new created system with 
            the (name,id) combination
            *Note* if not present the new System object will get the
            parameter o[name]:o.id

        db : data base, optional
            If db is None and parent is not None, db is taken from 
            parent.
            The data base is any object used to store configuration 
            of the all system. When a new system is created by a
            Collection object, for instance, the db is used to load
            the configuration parameters. It is usefull to have all
            the default parameter in one place. 
            Usually db is set only on the master system.  

        **kwargs : mappable, optional
            any key=value pair has parameter
        
        
        Examples
        --------
        db = {
                "tables" : {
                    "kitchen"   : {"width":100,"height":60},
                    "livingroom": {"width":200,"height":100}
                },
                "bottles" : {
                    "wine": {"alcool":True, "where":["livingroom"]},
                    "vinegar": {"alcool":True,  "where":["kitchen"]},
                    "wather":  {"alcool":False, "where":["kitchen", "livingroom"]},
                }
        }
        
        class Bottle(System):
            name = "bottle"

        class Bottles(Collection):
            name = "bottle"
            cls = Bottle

            def get_ids(self, parent):
                table = parent.get('table',None)
                if not table:
                    return parent.db['bottles'].keys()
                else:
                    for bottle, info in parent.db['bottles'].items():
                        if table in info['where']:
                            yield bottle
                    
            def get_parameters(self,parent, id):
                table = parent.get('table',None)
                if not table:
                    return parent.db['bottles'][id]
                info = parent.db['bottles'][id]
                if table not in info["where"]:
                    raise ValueError("bottle %r cannot be on table %r"%(id,table))
                return info
        
        class Table(System):
            name = "table"
            bottles = Bottles()

        class Tables(Collection):
            name = "table"
            cls = Table

            def get_ids(self, parent):
                return parent.db['tables'].keys()
            def get_parameters(self,parent, id):
                return parent.db['tables'][id]                                    
        

        class House(System):
            tables = Tables()
        


        >>> house = House(db=db)                    
        >>> house.tables("kitchen").bottles("wather")
        <system.base.Bottle at 0x11066c400 name='bottle' id='wather' >
        >>> house.tables("kitchen").bottles("wine")
        ValueError: bottle 'wine' cannot be on table 'kitchen'
        
        """
        name = name or self.name
        if name is None:
            name = self.__class__.lower()

        if id is None:
            id = self.parameters.get(name, kwargs.get(name,None) )
            
        if parent:
            path = parent.__path__.copy()
            try:
                pname = parent.name
            except AttributeError:
                pname = parent.__class__.__name__.lower()
            path[pname] = (parent.id, parent.parameters, parent.__class__)
            try:
                parameters, childs = parent.__childs__[(name,id)]
            except KeyError:
                parameters = self.Parameters(self.parameters)
                
                parameters.update(kwargs)
                childs = Childs()
                parent.__childs__[(name,id)] = (parameters, childs)
            else:
                parameters.update(kwargs)
                #if defaults:
                #    for k,v in defaults.items():
                #        parameters.setdefault(k,v)
            db = db or parent.db

        else:
            parameters = self.Parameters(self.parameters)             
            childs = Childs()
            path  = Path()

            if parameters:
                parameters = self.Parameters(parameters)
            else:
                parameters =  self.Parameters()

            parameters.update(kwargs)
            db = Db() if db is None else db

        if name and name!=ANONYMOUS:
            parameters.setdefault(name,id)

        self.parameters =  parameters
        self.__path__ =  path
        self.db = db        
        self.__childs__ = childs
        self.name = name
        self.id = id

    def __getitem__(self, item):

        if isinstance(item, tuple):
            if len(item)>1:
                raise KeyError("To many indices")
            truevalue = True
        else:
            truevalue = False

        try:
            v = self.parameters[item]
        except KeyError:
            for name, (id,d,c) in reversed(self.__path__.items()):
                try:
                    v = d[item]
                except KeyError:
                    pass
                else:
                    if hasattr(v, "__sget__"):
                        v = v.__sget__(self)
                        if truevalue:
                            return v
                        try:
                            cg = getattr(v, "__vget__")
                        except AttributeError:
                            return v
                        else:
                            return cg()                            
                    else:
                        return v
            else:
                raise KeyError('%r'%item)
        else:
            if hasattr(v, "__sget__"):
                v = v.__sget__(self)
                if truevalue:
                    return v
                try:
                    cg = getattr(v, "__vget__")
                except AttributeError:
                    return v
                else:
                    return cg()  
            else:
                return v

    def __setitem__(self, item, value):
        try:
            v =   self.parameters[item]
        except KeyError:            
            self.parameters[item] = value
        else:
            if hasattr(v, "__sget__") and not hasattr(v, "__sset__"):
                raise ValueError("%r parameter is read only"%item)
            self.parameters[item] = value    

    def __delitem__(self, item ):
        del self.parameters[item]


    def __repr__(self):
        return "<%s.%s at 0x%0x name=%r id=%r >"%(
                 globals()['__name__'],
                 self.__class__.__name__, 
                 id(self), 
                 self.name, 
                 self.id
                )

    @property
    def info(self):
        txt = ""
        for key, value in self.parameters.items():
            txt += '%s = %r\n'%(key, value)

        txt += "\n"
        tab = ""
        for name, (pid,d,c) in reversed(self.__path__.items()):
            txt += tab+"%s\n"%name
            txt += tab+"-"*len(name)+"\n"
            for key,value in d.items():
                txt += '%s%s = %r\n'%(tab, key, value)
            tab += " "*4
        return txt    

    


    def childs(self):
        find = set()

        for k,obj in self.__dict__.items():
            if isinstance(obj, Collection) and not obj.name in find:                                
                find.add(obj.name)
                yield obj.name

        for sub in self.__class__.__mro__:
            for k,obj in sub.__dict__.items():
                if isinstance(obj, Collection) and not obj.name in find:
                    find.add(obj.name)
                    yield obj.name      

    def child(self, name, id=None):
        for k,obj in self.__dict__.items():
            if isinstance(obj, Collection) and obj.name == name:
                return obj.__get__(self, self.__class__)(id)


        for sub in self.__class__.__mro__:
            for k,obj in sub.__dict__.items():
                if isinstance(obj, Collection) and obj.name == name:
                    return obj.__get__(self, self.__class__)(id)

        raise ValueError("cannot find child named %r"%name)

    def keys(self):
        """ iterator on keys parameters """
        return self.parameters.keys()

    def items(self):
        """ iterator on key,value pairs of parameters """
        return self.parameters.items()

    def values(self):
        """ iterator on parameters values """
        return self.parameters.values()

    def update(self, __d__={}, **kwargs):
        """ update parameters of system """
        self.parameters.update(__d__, **kwargs)

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

    def find(self, key):
        keys = key.split(".")
        key = keys[-1]
        for k in keys[:-1]:
            try:
                self = getattr(self, k)
            except AttributeError:
                raise KeyError('%r'%key)
        return self[key]

    def substitute(self, *args, **kwargs):
        mendatories = 0
        if args:
            if isinstance(args[0],int):
                mendatories = int(args[0])
                args = args[1:]
            else:
                mendatories = len(args)
        optionals = {}

        for i,a in enumerate(args):
            path, _, key = a.partition("->")

            if not key:
                key = path
            try:
                v = kwargs[key]
            except KeyError:
                pass
            else:
                if i<mendatories:
                    yield v
                else:
                    optionals[key] = v
                continue
            try:
                v = self.find(path)
            except KeyError:
                if i<mendatories:
                    raise ValueError("cannot subsitute %r argument by %r"%(key,path))
            else:
                if i<mendatories:
                    yield v
                else:
                    optionals[key] = v
        if len(args)!=mendatories:
            yield optionals


    def set_parent(self, parent):
        """ set a new parent for this system instance 

        Warning the child parameter will be update in the parent object.
        meaning that if child parameters has been modified somewhere else it will be lost
        """
        if self.db and (parent.db is not self.db):
            raise ValueError("parent does not share the same database")
        elif self.db is None:
            self.db = parent.db
                    
        path = parent.__path__.copy()
        try:
            pname = parent.name
        except AttributeError:
            pname = parent.__class__.__name__.lower()
        path[pname] = (parent.id, parent.parameters, parent.__class__)

        parent.__childs__[(self.name,self.id)] = (self.parameters, self.__childs__) 
        self.__path__ = path


    def parent(self, name=None):
        """ return the parent system of the given name 

        If does not exist raise ValueError
        """
        if name is None:
            pname = None
            for i,pname in enumerate(reversed(self.__path__)):                
                break
            if pname is None:
                raise StopIteration('')            

        else:
            for i,pname in enumerate(reversed(self.__path__)):
                if name==pname:
                    break
            else:            
                raise ValueError('Cannot find parent %r object'%(name))

        path = Path((pname,item) for (pname, item),j in zip(self.__path__.items(), range(len(self.__path__)-i-1)))

        id, d, C = self.__path__[pname]
        new = C(db=self.db, id=id, name=pname, **d)
        new.__path__ = path
        return new


    @classmethod
    def Pattern(cls, name=None, Parameters=None, **kwargs):
        return SystemPattern(cls=cls, name=name, Parameters=Parameters, **kwargs)

    @property
    def path(self):
        p = []
        for i,(pname,(pid,_,_)) in enumerate(self.__path__.items()):
            p.append((pname,pid))
        p.append((self.name, self.id))
        return "/"+("/".join(n if i is None else "%s:%s"%(n,i) for n,i in p[1:]))

    def goto(self, s):
        return goto(self, s)
    
###########################################################
#
#
#
class Collection(object):
    cls = System
    name = ANONYMOUS

    def __init__(self, parent=None,  name=None, cls=None, path=None):
        cls = self.cls if cls is None else cls
        name = self.name if name is None else name 
        if name is None or name==ANONYMOUS:
            name = getattr(cls, "name", ANONYMOUS)

        self.cls = cls
        self.parent = parent
        self.name = name
        
        if isinstance(path, basestring):
            path = [(n,None) for n in path.split(".")]
        if path is None:
            path = []
        self.path = path


    def ids(self):
        """ return iterator on available sub-sytems ids """
        parent = self.parent
        for n,i in self.path:
            parent = getattr(parent,n)(i)
        return self.get_ids(parent)

    def get_db(self, parent):    
        """ return the db associated to parent """    
        if parent is None:
            raise RuntImeError("Collection %r has no parent associated"%self.name)
        db = parent.db
        if db is None:
            raise RuntImeError("db is empty in parent of collection %r"%self.name)
        return db
    
    def get_ids(self, parend):
        raise RuntImeError("This collection has no iteration function")

    def get_parameters(self, parent, id):
        return {}

    def get_cls(self, parent, id):
        return self.cls

    def get_id(self, parent):
        return None

    def get(self, parent, id):
        if id is None:
            id = self.get_id(parent)

        if parent is None:            
            kw = self.get_parameters(parent, id)
            cls = self.get_cls(parent, id)
            return cls(name=self.name, id=id, **kw)

        try:
            parent.__childs__[(self.name, id)]
        except KeyError:
            pass
        else:
            return self.cls(parent=parent, name=self.name, id=id)

        kw = self.get_parameters(parent, id)
        cls = self.get_cls(parent, id)           
        # try:
        #     print(self.name, kw[self.name])
        #     parent.childs[(self.name, kw[self.name])]
        # except KeyError:
        #     pass
        # else:
        #     print("yes")
        #     return self.cls(parent=parent, name=self.name)
                
        return cls(parent=parent, name=self.name, id=id, **kw)

    def __call__(self, id=None, **kwargs):
        parent = self.parent
        for n,i in self.path:
            parent = getattr(parent,n)(i)

        child = self.get(parent, id)
        child.update(kwargs)        
        return child

    def __iter__(self):
        for id in self.ids():
            yield self(id)

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return CollectionInstance(obj, self)



class OneChild(Collection):
    """ A collection of only one system.
    
    Parameters can be defined as keywords argument, they will be the parameters
    when the system is ignitialized the first time.

    Example
    -------
    class Room(System):
        name = "room"
        tempsensors = OneChild(name="temp", id=0, description="temperature sensor")
    >>> Room().get_temp()    
    <system.base.System at 0x11204b978 name='temp' id=0 >

    class Room(System):
        name = "room"
        tempsensor = ChildProperty(OneChild(name="temp", id=0, description="temperature sensor"))
    >>> Room().tempsensor
    <system.base.System at 0x11204b470 name='temp' id=0 >
    """
    Parameters = Parameters
    parameters = Parameters()
    def __init__(self, name=None, id=None, cls=None, parent=None, path=None, **kwargs):
        Collection.__init__(self, parent=parent, cls=cls, name=name, path=path)
        self.parameters = self.Parameters(self.parameters)
        self.parameters.update(kwargs)
        self.id = id
    def get_id(self, parent):
        return self.id
    def get_ids(self, parent):
        yield self.id
    def get_parameters(self, parent, id):
        if id != self.id:
            raise ValueError("unique id %r does not match %r"%(self.id, id))
        return self.cls, self.parameters


class DbPointCollection(Collection):

    def __init__(self, dbpoint=None,  name=None, cls=None, parent=None, path=None, db=None):
        Collection.__init__(self, parent=parent, cls=cls, name=name, path=path)
        self.dbpoint = dbpoint
        self.db = db


    def get_ids(self, parent):
        if self.dbpoint is None:
            return iter([])
        db = self.parent.db if self.db is None else self.db
        return db.get(self.dbpoint,{}).keys()

    def get_parameters(self, parent, id):
        if self.dbpoint is None:
            return {}
        db = self.parent.db if self.db is None else self.db
        return db.get(self.dbpoint, {}).get(id, {})

    def get_id(self, parent):
        db = self.parent.db if self.db is None else self.db
        if self.dbpoint is None:
            raise ValueError("No default %s"%self.name)
        try:
            kw = db[self.dbpoint]
        except KeyError:
            raise ValueError("No default %s"%self.name)
        if len(kw)!=1:
            raise ValueError("No default %s"%self.name)
        id, = kw
        return id



class DbPoint2Collection(Collection):
    def __init__(self, dbpoint=None,  name=None, cls=None, parent=None, path=None, db=None):
        Collection.__init__(self, parent=parent, cls=cls, name=name, path=path)
        self.dbpoint = dbpoint
        self.db = db

    def get_ids(self, parent):
        if self.dbpoint is None:
            return iter([])
        db = self.parent.db if self.db is None else self.db
        db = db.get(self.dbpoint,{})
        return iter(db.get("table", {}))

    def get_parameters(self, parent, id):
        if self.dbpoint is None:
            return {}
        db = self.parent.db if self.db is None else self.db
        db = db.get(self.dbpoint,{})
        p = db.get("defaults", {})
        return dict(p, **db.get("table",{}).get(id,{}))

    def get_id(self, parent):
        db = self.parent.db if self.db is None else self.db
        if self.dbpoint is None:
            raise ValueError("No default %s"%self.name)
        try:
            db = db[self.dbpoint]
        except KeyError:
            raise ValueError("No default %s"%self.name)
        kw = db.get("table", {})
        if len(kw)!=1:
            raise ValueError("No default %s"%self.name)
        id, = kw
        return id


class LoockupCollection(Collection):
    def __init__(self, loockup=None, name=None, cls=None, path=None):
        Collection.__init__(self, cls=cls, name=name, path=path)
        self.loockup = {} if loockup is None else loockup

    def get_ids(self, parent):
        return iter(self.loockup)

    def get_parameters(self, parent, id):
        return self.loockup[id]

    def get_id(self, parent):
        if len(self.loockup)!=1:
             raise ValueError("No default %s"%self.name)
        id, = self.loockup
        return id

setattr(Collection, "from_dbpoint", DbPointCollection)
setattr(Collection, "from_dbpoint2", DbPoint2Collection)
setattr(Collection, "from_loockup", LoockupCollection)



class CollectionInstance(object):
    def __init__(self, parent, collection):
        self.parent = collection.parent or parent
        self.collection = collection

    def __call__(self, id=None, **kwargs):                        
        parent = self.parent
        for n,i in self.collection.path:
            parent = getattr(parent,n)(i)
        child = self.collection.get(parent, id)
        return child

    def __iter__(self):
        parent = self.parent
        for n,i in self.collection.path:
            parent = getattr(parent,n)(i)
        for id in self.collection.get_ids(self.parent):
            yield id

    # def ids(self):
    #     """ return iterator on available sub-sytems ids """
    #     parent = self.parent
    #     for n,i in self.collection.path:
    #         parent = getattr(parent,n)(i)

    #     return self.collection.get_ids(self.parent)

    # def get(self, id):
    #     parent = self.parent
    #     for n,i in self.collection.path:
    #         parent = getattr(parent,n)(i)
    #     return self.collection.get(parent, id)

    # def get_ids(self):
    #     return self.collection.get_ids(self.parent)
    
    # def get_parameters(self, id):
    #     return self.collection.get_parameters(parent)

    # def get_cls(self, parent):
    #     return self.collection.get_cls(parent)


def collection_parameters(cls=System, name=None, get_ids=None, path=None):        
    def decorate_collection(func):
        col = Collection(name=name, cls=cls, path=path)
        if get_ids:
            col.get_ids = get_ids
        col.get_parameters = func
        return col
    return decorate_collection

def collection(cls=System, name=None, get_ids=None, path=None):        
    def decorate_collection(func):
        col = Collection(name=name, cls=cls, path=path)
        if get_ids:
            col.get_ids = get_ids
        col.get = func
        return col
    return decorate_collection


def set_child_properties(cls, name_or_collection, ids, suffix=None):
    """ set several sub-system child properties to a class 

    Parameters
    ----------
    name_or_collection : string or Collection object
        if string this is the collection child name that can be found in the class instance.
    ids : iterable
        list of ids describing the sub-system
    suffix : string or None, optional
        by default (suffix=None) the attribute will be .{name}{id} where name is the name of
        the sub-system 
        if suffix is given the attribute will be .{suffix}{id}
    
    Examples
    --------
        
        tempSensors = LoockupCollection( {0:{'location':'ceilling'}, 
                                          1:{'location':'floor'}, 
                                          2:{'location':'window'} 
                                          }
                                        name = "tempsensor"
                                        ):
            
        class Room(System):
            tempSensors = tempSensors # this register a child named "tempsensor"

        set_child_properties(Room, "tempsensor", range(3), suffix="temp")

        >>> Room().temp0
        >>> Room().temp1
        
        rooms = LoockupCollection( {"bedroom":{}, "kitchen":{}}, name="room")
        class House(System):
            pass
        set_child_properties(House, rooms, ["bedroom", "kitchen"], suffix="")
        
        # is the same than doing:
        class House(System):
            bedroom = ChildProperty(rooms, "bedroom")
            kitchen = ChildProperty(rooms, "kitchen")
        
        # the later form is prefered in this case because more clear.

    """

    if isinstance(name_or_collection, Collection):
        name = name_or_collection.name            
    else:
        name = name_or_collection

    if suffix is None:
        suffix = name

    for id in ids:
        sid = "%s%s"%(suffix, id)
        setattr(cls, sid, ChildProperty(name_or_collection, id))

    # try:
    #     f = getattr(cls, colname)
    # except AttributeError:
    #     raise ValueError("class %s has no %r method "%(cls.__name__, colname))
    # else:
    #     if not hasattr(f, "__call__"):
    #         raise ValueError("method %r is not callable")

    # for id in ids:
    #     sid = "%s%s"%(suffix, id)        
    #     doc = "-> .%s(%r)"%(colname, id)
    #     setattr(cls, sid, property(lambda self, colname=colname, id=id:getattr(self,colname)(id), doc=doc))


def set_parent_properties(cls, parents):
    for parent in parents:
        setattr(cls, ParentProperty(parent))


class ChildProperty(object):
    def __init__(self, collection_or_string, id=None, doc=None):
        self.collection = collection_or_string
        self.id = id
        if doc is None:
            if isinstance(self.collection, basestring):
                doc = "-> %r of id %r"%(self.collection, id)
            else:
                doc = "-> %r of id %r"%(self.collection.name, id)
        self.__doc__ = doc

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        if isinstance(self.collection, basestring):
            return obj.child(self.collection, self.id)
        else:
            collection = self.collection.__get__(obj, obj.__class__)
        return collection(self.id)


class ParentProperty(object):
    def __init__(self, parent, doc=None):
        self.parent = parent
        if doc is None:
            doc = "-> .parent(%r)"%parent
        self.__doc__ = doc

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return obj.parent(self.parent)

###########################################################
##
## 
##



