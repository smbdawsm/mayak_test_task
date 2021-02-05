from flask import render_template, redirect, request
from app.lntranslator import translate_this, get_all_languages
from app import app
from app.monitor import monitoring_service
from app.models import Country, Type_Of_Server, Server, Language, Monitor
from flask import jsonify
import flask
import json
from datetime import datetime

from flask_cors import cross_origin, CORS

cors = CORS(app, resources={r"/*": {"origins": "*"}})


API_KEY = '84fi2j4lfk42fj204u2lkfnsdjsak433'

#######################################
######### Block Countries #############


@app.route('/api/country/all', methods=['get'])
@cross_origin()
def get_all_coutries():
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    '''Выводит список стран с инфраструктурой '''
    all_countries = Monitor.objects.all()
    res = {}
    for coun in all_countries:
        if coun.alive == True and coun.type_server == 'gtn_farhub':
            res[coun.location] = coun.to_json()
    return json.dumps(res, indent=1, sort_keys=True, default=str)

@app.route('/api/country/select', methods=['post'])
@cross_origin()
def get_country():
    ''' Выводит инфраструктуру с поисковиками и переводчиками по стране '''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    json_data = request.get_json(force=True)
    try: 
        country = Country.objects.get(name=json_data['country'])
        response = country.to_json_on_front()
        return jsonify(response)
    except Exception as err:
        return f'{datetime.now()} Incorrect Query! ERROR in app: Exception on /api/country/select [GET] \n{err}', 400

@app.route("/api/country/add/<country_name>", methods=["get"]) 
@cross_origin()
def create_country(country_name):
    '''Создает страну'''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    if country_name is None or not country_name:
        return 'Incorrect Query'
    try:
        country = Country.objects.get(name=country_name)
        return 'Объект существует'
    except Exception:
        country = Country(name=country_name)
        country.save() 
    return '200 OK'

#######################################
########## Block Servers ##############


@app.route('/api/server/all', methods=['get'])
@cross_origin()
def get_all_servers():
    '''Выдает информацию о всех серверах'''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    all_servers = {}
    for srv in Server.objects.all():
        all_servers[srv.hash_id] = srv.to_json()
    return jsonify(all_servers)

##############################################
############## Block Translate ###############

@app.route('/api/translate_query', methods=['post'])
@cross_origin()
def translate_api():
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    json_data = request.get_json(force=True)
    json_data['query'] = translate_this(json_data['query'], src_lang=json_data['src_lang'], to_lang=json_data['to_lang']) 
    return jsonify(json_data)
    
@app.route('/api/translate/all', methods=['get'])
@cross_origin()
def all_lang_list():
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    return jsonify(get_all_languages())

##############################################
############## Block Langs ###################

@app.route('/api/langs/<name>', methods=['get'])
@cross_origin()
def return_langs_list_for_country(name):
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    country = Country.objects.get(name=name)
    response = country.lang_return()
    return jsonify(response)

@app.route('/api/langs/<short>/<full>/<name>', methods=['get'])
@cross_origin()
def add_language(short, full, name):
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    lang = Language(short=short, full=full, name=name)
    lang.save()
    return '200 OK'

###############################################
############## Block Groups ################### 

@app.route("/api/groups/<tosname>", methods=["get"])
@cross_origin()
def create_group(tosname):
    """Создает группу для серверов"""
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    if tosname is None or not tosname:
        return 'Incorrect Query'
    tos = Type_Of_Server(type_of_server=tosname)
    tos.save()
    return '200 OK'

###############################################
############## GTN FARHUB ##################### 

@app.route("/gtnfarhub/countries/add", methods=["post"])
@cross_origin()
def create_server():
    '''Создает сервер типа farhub '''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    json_data = request.get_json(force=True)

    try: 
        srv = Server.objects.get(hash_id=json_data['hash_id'])
        srv.delete()
    except Exception:
        pass
    finally:   
        try: 
            coun = Country.objects.get(name=json_data['location'])
        except:
            coun = Country(name=json_data['location'])
            coun.save()
        try:
            server_name = Type_Of_Server.objects.get(type_of_server='gtn_farhub')
        except:
            server_name = Type_Of_Server(type_of_server='gtn_farhub')
            server_name.save()
        server = Server(type_of_server=server_name,address=json_data['server_ip'],location=coun, api_key=json_data['api_key'],
                         data = json_data['data'], description=json_data['description'], hash_id=json_data['hash_id'])
        server.save() 
        Country.synhro()
        monitoring_service()
        return '200 OK'

@app.route('/gtnfarhub/countries/show', methods = ['get'])
@cross_origin()
def show_gntfarhubs():
    '''Показывает gtnfarhub по странам'''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    all_countries = Country.objects.all()
    res = {}
    for coun in all_countries:
        res[coun.name] = [srv.for_farhub() for srv in coun.servers]
    return flask.jsonify(res), 200

@app.route('/gtnfarhub/server/delete', methods = ['post'])
@cross_origin()
def delete_farhub():
    '''удаляет сервер gtnfarhub'''
    if (API_KEY != request.args.get('api')):
        return jsonify({'error': 'Wrong api key'}), 400
    json_data = request.get_json(force=True)
    try:
        srv = Server.objects.get(hash_id=json_data['hash_id'])
        coun = Country.objects.get(name=srv.location.name)
        coun.servers.pop(srv.location.servers.index(Server.objects.get(address=srv.address)))
        coun.save()
        srv.delete()
        return 'OK', 200
    except Exception as err:
        return f'{datetime.now()} Incorrect Querry! Exception {err}', 400