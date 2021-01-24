import flask
import requests
import time
from datetime import timedelta

from redis import Redis
from rq import Queue
from rq.decorators import job
from app import app
from app.models import Monitor, Server, Country
from flask_login import login_required, current_user

redis_conn = Redis()
q = Queue(name='high', connection=redis_conn)

@job('high', connection=redis_conn, timeout=5)
def healthcheck(ip, port):
    try: 
        srv = Monitor.objects.get(ip=ip)
        url = f'http://{ip}:{port}/api/sys/ping'
        resp = requests.get(url, timeout=5).json()
        if resp['success'] == 'success':
            srv.alive = True
            srv.save()
        else:
            srv.alive = False
            srv.save()
    except Exception:
        print('FAILED')
        srv.alive = False
        srv.save()


def monitoring_service():
    response = []
    for srv in get_all_server_objects():
        if srv.type_server == 'gtn_farhub':
            port = 8000
        job = healthcheck.delay(srv.ip, port)
        temp = [srv.location, srv.type_server, srv.ip, srv.alive]
        response.append(temp)
    return response

@app.route('/monitor', methods=['get'])
def monitor():
    active = 'active'
    monitoring_service()
    response = Monitor.objects.all()
    return flask.render_template('main.html', response = response, active = active, name=current_user.name)


def get_all_server_objects():
    result_list = []
    all_servers = {}
    for srv in Server.objects.all():
        all_servers[srv.hash_id] = srv.to_json()
    resp = all_servers
    for k, v in resp.items():
        try:
            monitoring = Monitor.objects.get(hash_id=v['hash'])
            monitoring.ip = v['host']
            monitoring.location = v['location']
            monitoring.type_server = v['type']
            monitoring.description = v['description']
            monitoring.save()
        except Exception:
            monitoring = Monitor(hash_id=v['hash'], ip=v['host'], location=v['location'], type_server=v['type'], description=v['description']).save()
        result_list.append(monitoring)
    current_srvs = Monitor.objects.all()
    print('info updated')
    for srv in current_srvs:
        if srv not in result_list:
            srv.delete()
    return result_list
