from flask import Flask

app = Flask(__name__)
app.config.from_object('app.config')
app.config['MONGODB_SETTINGS'] = {
    'db': 'textbase',
    'host': 'localhost',
    'port': 27017,
    'connect': False
}
from app import views
from app import monitor
from app import apirequests



