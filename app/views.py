from flask import render_template, redirect, request
from app import app
from app.mongo import Database

@app.route('/', methods=['post', 'get'])
def index():
    message = ''
    if request.method == 'POST':
        key = request.form.get('key')
        text = request.form.get('text')
        if (key != '') and text != '':
            d = Database()
            data = {key: text}
            d.insert_document(d.objects_collection, data)
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