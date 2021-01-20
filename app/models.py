from flask_mongoengine import MongoEngine
from app import app

db = MongoEngine()
db.init_app(app)


class Monitor(db.Document):

    hash_id = db.StringField(unique=True)
    location = db.StringField()
    ip = db.StringField()
    type_server = db.StringField()
    alive = db.BooleanField()
    description = db.StringField()



class Type_Of_Server(db.Document):

    type_of_server = db.StringField(unique=True)
    servers = db.ListField(db.ReferenceField('Server'))
    
    #Function for synhronize data in DB for actual information about servers.
    @staticmethod
    def synhro():
        for server in Server.objects.all():
            try:
                types = Type_Of_Server.objects.get(name = server.type_of_server.name)
                if server not in types.servers:
                    types.servers.append(server)
                    types.save()
            except Exception as err:
                print(err)
        return None

class Server(db.Document):


    hash_id = db.StringField()
    type_of_server = db.ReferenceField('Type_Of_Server')
    address = db.StringField(unique=True)
    location = db.ReferenceField('Country')
    description = db.StringField(default='')
    full_description = db.StringField(default='')
    data = db.DictField()
    
    def to_json(self):
        return {
            
            "type": self.type_of_server.type_of_server,
            "host": self.address,
            'location': self.location.name,
            "description": self.description,
            'hash': self.hash_id,
            'data': self.data
        
        }
    
    def for_farhub(self):
        print(Monitor.objects.get(hash_id=self.hash_id).alive)
        return { self.hash_id: {
            "IP": self.address,
            "description": self.description,
            'data': self.data,
            'alive': Monitor.objects.get(hash_id=self.hash_id).alive
        }
        }

class Searcher(db.Document):

    name = db.StringField(unique=True)
    country = db.ReferenceField('Country')
    text = db.BooleanField()
    img = db.BooleanField()
    video = db.BooleanField()

    def to_json(self):
        return {
            'name': self.name,
            'location': self.country.name,
            'text': self.text,
            'img': self.img,
            'video': self.video
        }

class Country(db.Document):

    name = db.StringField(unique=True)
    servers = db.ListField(db.ReferenceField('Server'))
    langs = db.ListField(db.ReferenceField('Language'))

    def lang_return(self):
        res = {}
        for lang in self.langs:
            res[lang.short]= { 'sublang': lang.full,
                                'name': lang.name}
        return res

    def to_json(self):
        return {
            'Location': self.name,
            'Counter': len(self.servers),
            'IP address': [srv.address for srv in self.servers],
            'lang': [lang.full for lang in self.langs]
        }

    def to_json_on_front(self):
        return {
            'Location': self.name,
            'Counter': len(self.servers),
            'Servers': [srv.for_farhub() for srv in self.servers],
            'lang': [lang.full for lang in self.langs]
        }    
    
    @staticmethod
    def synhro():
        for country in Country.objects.all():
            country.servers = []
            print(country.name)
            for srv in Server.objects.all():
                print(srv.location.name)
                if srv.location.name == country.name:
                    
                    country.servers.append(srv)
                    country.save()
        return 'fin'


class Language(db.Document):

    short = db.StringField()
    full = db.StringField()
    name = db.StringField()
    countries = db.ListField(db.ReferenceField('Country'))

    def to_json(self):
        return {
            'short': self.short,
            'full': self.full,
            'name': self.name,
            'countries': [country.name for country in self.countries]
        }
