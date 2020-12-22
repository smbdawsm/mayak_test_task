from flask import render_template, redirect, request
from app import app
from app.mongo import Database
from flask_mongoengine import MongoEngine
from bson.objectid import ObjectId
from translate import Translator
from langdetect import detect


db = MongoEngine()
db.init_app(app)

class Type_Of_Server(db.Document):
    type_of_server = db.StringField(unique=True)

class Country(db.Document):

    name = db.StringField(unique=True) #unique=True

    def counter_servers(self):
        all_list = Country.objects.all()
        count_of_servers = len(all_list)
        return count_of_servers


class Server(db.Document):

    type_of_server = db.ReferenceField(Type_Of_Server)
    address = db.StringField(unique=True)
    location = db.ReferenceField(Country)
    description = db.StringField(default='')
    full_description = db.StringField(default='')
    
    def to_json(self):
        return {
            "type": self.type_of_server.type_of_server,
            "host": self.address,
            'location': self.location.name,
            "description": self.description,
            "full_description": self.full_description
        }

@app.route('/translate/<to_lang>/<query>/<from_lang>', methods=['get'])
def translate_this(to_lang, query, from_lang):
    source_lang = detect(query)
    if from_lang is None or not from_lang:
        from_lang = source_lang
    trans = Translator(from_lang=from_lang,to_lang=to_lang)
    translated = trans.translate(query)
    return translated

@app.route('/allservers', methods=['get'])
def get_all_servers_view():
    servers = Server.objects.all()
    all_srv_list = []
    for srv in servers:
        all_srv_list.append(srv.to_json())
    return render_template('allservers.html', all_srv_list=all_srv_list)

@app.route('/countries', methods=['post', 'get'])
def country_view():
    message = ''
    text_list = {}
    country_list = Country.objects.all()
    for country in country_list:
        counter = 0
        ip_list = []
        servers = Server.objects.filter(location=country)
        try:
            for srv in servers:
                if srv.location.name == country.name:
                    counter += 1
                    ip_list.append(srv.address)
                else:
                    print('miss')
        except:
            print() 
        text_list[country.name] = (counter, ip_list)
    return render_template('countries.html', text_list = text_list, message = message)

@app.route('/groups', methods=['get'])
def groups_list():
    message = ''
    text_list = {}
    groups = Type_Of_Server.objects.all()
    print(groups)
    for group in groups:
        counter = 0
        ip_list = []
        servers = Server.objects.filter(type_of_server=group)
        try:
            for srv in servers:
                print(srv.type_of_server.type_of_server, group.type_of_server)
                if srv.type_of_server.type_of_server == group.type_of_server:
                    counter += 1
                    ip_list.append(srv.address)
        except:
            pass
            
        text_list[group.type_of_server] = (counter, ip_list)    

    return render_template('groups.html', text_list = text_list)

@app.route('/server', methods=['post', 'get'])
def server_list():

    color = 'aqua'
    message = ''
    if request.method == 'POST':
        type_of_server = request.form.get('type_of_server')
        address = request.form.get('address')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        location = request.form.get('location')
        
        
        if (type_of_server != '') and (address != ''):
            try:
                coun = Country.objects.get(name=location)
                print(coun.name)
            except: 
                coun = Country(name=location)
                coun.save()
                print(coun.name)
            try:
                application = Type_Of_Server.objects.get(type_of_server=type_of_server)
            except:
                application = Type_Of_Server(type_of_server=type_of_server)
                application.save()
            srv = Server(type_of_server=application,address=address,description=description, location=coun, full_description=full_description)
            srv.save()
            message = 'success'
        else:
            color = 'red'
            message = 'You must type anything!'
    return render_template('server.html', message = message, color = color)


@app.route("/countries/<country_name>", methods=["get"])
def create_country(country_name):
    if country_name is None or not country_name:
        return 'Incorrect Query'
    country = Country(name=country_name)
    country.save() 
    return '200 OK'

@app.route("/server/<server_name>/<host>/<location>/<description>", methods=["get"])
def create_server(server_name, host, location, description=""):
    if (server_name is None or not server_name) and (host is None or not host) and location is None or not location :
        return 'Incorrect Query'
    try: 
        coun = Country.objects.get(name=location)
    except:
        coun = Country(name=location)
        coun.save()
    try:
        server_name = Type_Of_Server.objects.get(type_of_server=server_name)
    except:
        server_name = Type_Of_Server(type_of_server=server_name)
        server_name.save()
    server = Server(type_of_server=server_name,address=host,location=coun, description=description)
    server.save() 
    return '200 OK'

@app.route('/edit_server/<host>', methods=['post', 'get'])
def server_edit(host):
    print(host)
    srv = Server.objects.get(address=host)
    color = 'aqua'
    message = ''
    info = srv.to_json()
    print(info)
    if request.method == 'POST':
        type_of_server = request.form.get('type_of_server')
        address = request.form.get('address')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        location = request.form.get('location')
        try:
            coun = Country.objects.get(name=location)
            print(coun.name)
        except: 
            coun = Country(name=location)
            coun.save()
            print(coun.name)
        try:
            application = Type_Of_Server.objects.get(type_of_server=type_of_server)
        except:
            application = Type_Of_Server(type_of_server=type_of_server)
            application.save()
        srv.type_of_server = application
        srv.address = address
        srv.description = description
        srv.location = coun
        srv.full_description = full_description
        srv.save()
        message = 'success'
    return render_template('editserver.html', message = message, color = color, info = info)

@app.route('/server_search', methods=['post', 'get'])
def server_search():
    info = ''
    message = ''
    if request.method == 'POST':
        address = request.form.get('address')
        print(address)
        if address != '':
            print(address)
            try: 
                srv = Server.objects(address=address).first()
                for k, v in srv.to_json().items():
                    info += '\n' + k + ' : ' + v + '\n'
            except:
                message = f'Have not entry: {address} in DB'
        else:
            message = 'Insert a key!'
    return render_template('server_search.html', message=message, info=info)

@app.route('/', methods=['post', 'get'])
def index():
    message = ''
    if request.method == 'POST':
        key = request.form.get('key')
        text = request.form.get('text')
        a = Link('http://127.0.0.1:5000', 'this is my APP', 'My Flask Application')
        if (key != '') and text != '':
            d = Database()
            data = {key: text}
            d.insert_document(d.objects_collection, data)
            message = a.description
        else:
            message = 'You must type anything!'
    return render_template('index.html', message = message)

@app.route ('/search', methods= ['post', 'get'])
def search():
    text = ''
    message = ''
    data = ''
    if request.method == 'POST':
        key = request.form.get('key')
        if key != '':
                d = Database()
                data = d.find_document(d.objects_collection, {key : {'$exists': 1}} , multiple=True)
                if data != []:
                    text = data[0][key]
                else:
                    message = 'Incorrect query'
                
        else:
            message = 'Insert a key!'

    return render_template('search.html', message = message, data = text)
