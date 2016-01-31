from application import *
from flask import Flask, render_template, request, abort, redirect, url_for, flash, Response, jsonify, get_flashed_messages, session
from application.slave_poll import *
from application.slave import *
from application.models import *
import datetime

if app.config['MODE'] == 'master':

    testroles_row = testroles.query.filter(testroles.testrole_order == 1).order_by(testroles.id).first()
    testroles_row.slave_id = 0
    db.session.commit()

    @app.route('/')
    def index_master():

        print(get_latest_commit())

        slave_res = slaves.query.filter().order_by(slaves.slave_hostname).all()
        return render_template('index.html', slave_res=slave_res)

    @app.route('/os')
    def os():
        return str(get_system_info())

    @app.route('/master/slave_update', methods=['POST'])
    def master_slave_update():
        request_json = request.get_json(force=True)

        print(request_json)

        ## Insert/Update Slave Details
        slave_row = slaves.query.filter(slaves.slave_hostname == request_json['system_info']['hostname'], slaves.slave_ip == request_json['system_info']['ip']).order_by().first()
        if slave_row:
            slave_row.slave_last_connect = datetime.datetime.now()
            slave_row.test_id = request_json['test_id']
        else:
            slave_row = slaves(request_json['system_info']['hostname'], request_json['system_info']['version'], request_json['system_info']['system'], request_json['system_info']['cores'], request_json['system_info']['distribution'], request_json['system_info']['ip'], datetime.datetime.now())
            db.session.add(slave_row)
        db.session.commit()

        available_processes = int(request_json['system_info']['cores'])

        data = {}
        data['status'] = 1

        test_row = tests.query.filter().order_by(tests.id.desc()).first()
        if test_row:
            data['test_id'] = test_row.id
        else:
            data['test_id'] = 0

        data['test_roles'] = []

        # Only do the next step if every alive slave has updated its test id

        alive_time = datetime.datetime.now() - datetime.timedelta(seconds=240)
        alive_slaves = slaves.query.filter(slaves.slave_last_connect > alive_time, slaves.test_id != data['test_id']).order_by().all()

        if len(alive_slaves) == 0:
            testrolesorder_row = testroles.query.filter(testroles.test_id == data['test_id'], testroles.testrole_status != 2).order_by(testroles.testrole_order).first()
            if testrolesorder_row:
                testrole_order = testrolesorder_row.testrole_order
                testroles_res = testroles.query.filter(testroles.test_id == data['test_id'], testroles.slave_id == 0, testroles.testrole_order == testrole_order).order_by(testroles.id).limit(available_processes).all()
                for testroles_row in testroles_res:
                    data['test_roles'].append({'id': testroles_row.id, 'name': testroles_row.testrole_name, 'type': testroles_row.testrole_type } )
                    testroles_row.slave_id = slave_row.id
                    db.session.commit()

                    # TODO: Assign slave_id to this node

        return Response(json.dumps(data),  mimetype='application/json')



    def get_latest_commit():

        response = requests.get('https://api.github.com/repos/landregistry-ops/puppet-control')
        response_json = response.json()
        print(response_json)
        if 'pushed_at' in response_json:
            pushed_date = datetime.datetime.strptime(response_json['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")

            test_row = tests.query.filter(tests.test_pushedat == pushed_date).order_by().first()
            if not test_row:
                test_row = tests(pushed_date)
                db.session.add(test_row)
                db.session.commit()
                test_id = test_row.id

                response = requests.get('https://api.github.com/repositories/29131296/contents/hiera/roles')
                response_json2 = response.json()

                db.session.add(testroles(test_id, 'puppet-master', 1, 1))

                for files in response_json2:
                    db.session.add(testroles(test_id, files['name'], 2, 2))

                db.session.commit()


                return test_id

            return 0

            print(res)
        else:
            return 0

#

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
