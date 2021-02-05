from flask_mongoengine import MongoEngine
from app import app
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy


db = MongoEngine()
db.init_app(app)

users_db = SQLAlchemy()
users_db.init_app(app)

class User(UserMixin, users_db.Model):
    id = users_db.Column(users_db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = users_db.Column(users_db.String(100), unique=True)
    password = users_db.Column(users_db.String(100))
    name = users_db.Column(users_db.String(1000))

class Monitor(db.Document):

    hash_id = db.StringField(unique=True)
    location = db.StringField()
    ip = db.StringField()
    type_server = db.StringField()
    alive = db.BooleanField()
    description = db.StringField()

    def to_json(self):
        return {
            'hash_id': self.hash_id,
            'ip': self.ip,
            'type_server': self.type_server,
        }


class Type_Of_Server(db.Document):

    type_of_server = db.StringField(unique=True)
    servers = db.ListField(db.ReferenceField('Server'))
    
    #Function for synhronize data in DB for actual information about servers.
    @staticmethod
    def synhro():
        for server in Server.objects.all():
            try:
                types = Type_Of_Server.objects.get(type_of_server = server.type_of_server.type_of_server)
                if server not in types.servers:
                    types.servers.append(server)
                    types.save()
            except Exception as err:
                print(err)
        return None

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
            'location': self.name,
            'counter': len(self.servers),
            'ip address': [srv.address for srv in self.servers],
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
            for srv in Server.objects.all():
                if srv.location.name == country.name:
                    
                    country.servers.append(srv)
                    country.save()
        return 'fin'


class Server(db.Document):
    '''Description Server class '''
    api_key = db.StringField()

    hash_id = db.StringField(unique=True)
    type_of_server = db.ReferenceField('Type_Of_Server')
    address = db.StringField()
    location = db.ReferenceField('Country', reverse_delete_rule=db.NULLIFY)
    description = db.StringField(default='')
    full_description = db.StringField(default='')
    data = db.DictField()
    
    def to_json(self):
        try:
            response = {
            
            "type": self.type_of_server.type_of_server,
            "host": self.address,
            'location': self.location.name,
            "description": self.description,
            'hash': self.hash_id,
            'data': self.data
        
        }
        except Exception:
            response = {
            
            "type": self.type_of_server.type_of_server,
            "host": self.address,
            'location': self.location,
            "description": self.description,
            'hash': self.hash_id,
            'data': self.data
        
        }

        return response


    def for_farhub(self):
        print(Monitor.objects.get(hash_id=self.hash_id).alive)
        return { self.hash_id: {
            "ip": self.address,
            "description": self.description,
            'data': self.data,
            'api_key': self.api_key,
            'alive': Monitor.objects.get(hash_id=self.hash_id).alive
        }
        }




class Searcher(db.Document):

    engine = db.StringField(unique=True)
    icon = db.StringField()
    text = db.BooleanField(default=False)
    img = db.BooleanField(default=False)
    video = db.BooleanField(default=False)
    cat = []

    def to_json(self):
        self.cat = []
        if self.text == True and 'general' not in self.cat :
            self.cat.append('general')
        if self.img == True and 'images' not in self.cat :
            self.cat.append('images')
        if self.video == True and 'videos' not in self.cat:
            self.cat.append('videos')
        return {
            'engine': self.engine,
            'icon': self.icon,
            'categories': self.cat
        }


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
