from application import *
from flask import Flask, render_template, request, abort, redirect, url_for, flash, Response, jsonify, get_flashed_messages, session
from application.poll import *
from application.slave import *
from application.models import *
import datetime

if app.config['MODE'] == 'master':

    @app.route('/')
    def index_master():
        slave_res = slaves.query.filter().order_by(slaves.slave_hostname).all()
        return render_template('index.html', slave_res=slave_res)

    @app.route('/os')
    def os():
        return str(get_system_info())

    @app.route('/master/slave_update', methods=['POST'])
    def master_slave_update():
        request_json = request.get_json(force=True)


        ## Insert/Update Slave Details
        slave_row = slaves.query.filter(slaves.slave_hostname == request_json['system_info']['hostname'], slaves.slave_ip == request_json['system_info']['ip']).order_by().first()
        if slave_row:
            slave_row.slave_last_connect = datetime.datetime.now()
        else:
            slave_row = slaves(request_json['system_info']['hostname'], request_json['system_info']['version'], request_json['system_info']['system'], request_json['system_info']['cores'], request_json['system_info']['distribution'], request_json['system_info']['ip'], datetime.datetime.now())
            db.session.add(slave_row)
        db.session.commit()

        return Response(json.dumps({'status': 1}),  mimetype='application/json')

elif app.config['MODE'] == 'slave':

    @app.route('/')
    def index_slave():
        return str(get_system_info())


def is_datetime_recently(value):
    current_dateime = value + datetime.timedelta(seconds=60)
    if (datetime.datetime.now() < current_dateime):
        return 1
    else:
        return 0

app.jinja_env.globals.update(is_datetime_recently=is_datetime_recently)
