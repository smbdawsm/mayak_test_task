from flask import render_template, redirect, request
from app import app
from app.mongo import Database
from flask_mongoengine import MongoEngine


db = MongoEngine()
db.init_app(app)

class Type_Of_Server(db.Document):
    type_of_server = db.StringField()

application = Type_Of_Server(type_of_server='Application server')
application.save()

class Server(db.Document):

    type_of_server = db.ReferenceField(Type_Of_Server)
    address = db.StringField()
    description = db.StringField()
    full_description = db.StringField()
    
    def to_json(self):
        return {
            "type": self.type_of_server.type_of_server,
            "host": self.address,
            "description": self.description,
            "full_description": self.full_description
        }

@app.route('/server', methods=['post', 'get'])
def server():
    message = ''
    if request.method == 'POST':
        type_of_server = request.form.get('type_of_server')
        address = request.form.get('address')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        
        if (type_of_server != '') and (address != '') and (type_of_server == 'Application'):
            srv = Server(type_of_server=application,address=address,description=description, full_description=full_description)
            srv.save()
            message = 'success'
        else:
            message = 'You must type anything!'
    return render_template('server.html', message = message)

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
