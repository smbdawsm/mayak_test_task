from flask import render_template, redirect, request, jsonify
from app import app
from app.monitor import monitoring_service
from app.models import Country, Type_Of_Server, Server, Language
import flask
import requests
import string
import random

monitoring_service()
Country.synhro()
Type_Of_Server.synhro()


@app.route('/', methods=['post', 'get'])
@app.route('/allservers', methods=['get'])
def get_all_servers_view():
    servers = Server.objects.all()
    all_srv_list = []
    for srv in servers:
        for_view = srv.to_json()
        for_view.pop('data', None)
        all_srv_list.append(for_view)
    return render_template('allservers.html', all_srv_list=all_srv_list)

@app.route('/countries', methods=['post', 'get'])
def country_view():
    Country.synhro()
    message = ''
    text_list = []
    country_list = Country.objects.all()
    for country in country_list:
        text_list.append(country.to_json())
        print(text_list)
    print(country_list)
    return render_template('countries.html', text_list = text_list, message = message, country_list=country_list)

@app.route('/groups', methods=['get'])
def groups_list():
    Type_Of_Server.synhro()
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
    types = Type_Of_Server.objects.all()
    countries = Country.objects.all()
    color = 'aqua'
    message = ''
    if request.method == 'POST':
        type_of_server = request.form.get('type_of_server')
        address = request.form.get('address')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        location = request.form.get('location')
        type_server = Type_Of_Server.objects.get(type_of_server=type_of_server)
        coun = Country.objects.get(name=location)
        hash_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
        if address != '':
            srv = Server(type_of_server=type_server,address=address,description=description, location=coun, full_description=full_description, hash_id=hash_id)
            srv.save()
            Country.synhro()
            monitoring_service()
            message = 'success'
        else:
            color = 'red'
            message = 'You must type anything!'
    return render_template('server.html', message = message, color = color, countries = countries, types=types)

@app.route('/edit_server/<host>', methods=['post', 'get'])
def server_edit(host):
    types = Type_Of_Server.objects.all()
    countries = Country.objects.all()
    srv = Server.objects.get(address=host)
    prev = srv.location.name
    cont = Country.objects.get(name=prev)
    #this FOR deletes old info about Country, when location Server changes
    for el in cont.servers:
        print(el)
        if el.address == srv.address:
            cont.servers.pop(cont.servers.index(el)) 
            cont.save()
    color = 'aqua'
    message = ''
    info = srv.to_json()
    if request.method == 'POST':
        type_of_server = request.form.get('type_of_server')
        address = request.form.get('address')
        description = request.form.get('description')
        full_description = request.form.get('full_description')
        location = request.form.get('location')
        coun = Country.objects.get(name=location)
        application = Type_Of_Server.objects.get(type_of_server=type_of_server)
        srv.type_of_server = application
        srv.address = address
        srv.description = description
        srv.location = coun
        srv.full_description = full_description
        srv.save()
        message = 'success'
    return render_template('editserver.html', message = message, color = color, info = info, countries = countries, types=types)

@app.route('/edit_country/<name>', methods=['post', 'get'])
def edit_country(name):
    langs = Language.objects.all()
    country = Country.objects.get(name=name)
    info = country.to_json()
    if request.method == 'POST':
        name = request.form.get('name')
        lang = request.form.get('lang')
        print(lang)
        l = Language.objects.get(name = lang)
        country.name = name
        if l not in country.langs:
            country.langs.append(l)
        country.save()

    return render_template('editcountry.html', langs=langs, info=info)


@app.route('/countries/<name>/delete', methods=['get'])
def delete_country_obj(name):
    country = Country.objects.get(name=name)
    country.delete()
    return render_template('delete.html')

@app.route('/server/<host>/delete', methods=['get'])
def delete_server_obj(host):
    
    srv = Server.objects.get(address=host)
    coun = Country.objects.get(name=srv.location.name)
    coun.servers.pop(srv.location.servers.index(Server.objects.get(address=srv.address)))
    coun.save()
    srv.delete()
    
    return render_template('delete.html')


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

@app.route('/faq', methods=['get'])
def faq():
    return render_template('f1.html')

@app.route('/parsers', methods=['get'])
def show_parsers():
    result = {}
    farhub_tos = Type_Of_Server.objects.get(type_of_server='gtn_farhub')
    farhub_servers = Server.objects.filter(type_of_server=farhub_tos)
    for srv in farhub_servers:
        result[srv.address] = srv.data
        for aggr in srv.data['aggregators']:
            print(aggr)
    return jsonify(result)