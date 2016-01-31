from application import *
from flask import Flask, render_template, request, abort, redirect, url_for, flash, Response, jsonify, get_flashed_messages, session
from application.polling import *
from application.slave import *
from application.models import *
import datetime
import ansiconv

if app.config['MODE'] == 'master':

    destroy_all_vms()
    stop_command = False

    # TODO: Must remove!
    # testroles_row = testroles.query.filter(testroles.testrole_order == 1).order_by(testroles.id).first()
    # testroles_row.slave_id = 0
    # testroles_row.testrole_status = 0
    # db.session.commit()

    @app.route('/')
    def index_master():

        #print(get_latest_commit())

        slaves_array = {}
        slaves_res = slaves.query.filter().order_by(slaves.id.desc()).all()
        for slaves_row in slaves_res:
            slaves_array[slaves_row.id] = slaves_row.slave_hostname



        test_row = tests.query.filter().order_by(tests.id.desc()).first()
        if test_row:
            test_id = test_row.id
        else:
            test_id = 0

        testroles_res = testroles.query.filter(testroles.test_id == test_id).order_by(testroles.id).all()

        slave_res = slaves.query.filter().order_by(slaves.slave_hostname).all()
        return render_template('index.html', slave_res=slave_res, test_row=test_row, test_id=test_id, testroles_res=testroles_res, slaves_array=slaves_array)

    @app.route('/os')
    def os():
        # TODO: Must remove!
        testroles_row = testroles.query.filter(testroles.testrole_order == 1).order_by(testroles.id).first()
        testroles_row.slave_id = 0
        testroles_row.testrole_status = 0
        db.session.commit()

        return str(get_system_info())


    @app.route('/log/<id>')
    def log(id):

        testroles_row = testroles.query.filter(testroles.id == id).order_by(testroles.id).first()
        html = ansiconv.to_html(testroles_row.testrole_log)
        css = ansiconv.base_css()
        return render_template('logs.html', testroles_row=testroles_row, html=html, css=css)


    @app.route('/new_test')
    def new_test():
        test_row = tests.query.filter().order_by(tests.id.desc()).first()

        if test_row:
            test_id = test_row.id
            new_test_row = tests(test_row.test_pushedat)
            db.session.add(new_test_row)
            db.session.commit()
            new_test_id = new_test_row.id
            testroles_res = testroles.query.filter(testroles.test_id == test_id).order_by(testroles.id).all()

            for testrole_row in testroles_res:
                db.session.add(testroles(new_test_id, testrole_row.testrole_name, testrole_row.testrole_order, testrole_row.testrole_type, testrole_row.testrole_ipnum))

            db.session.commit()

        return redirect(url_for('index_master'))

    @app.route('/master/slave_update', methods=['POST'])
    def master_slave_update():
        request_json = request.get_json(force=True)

        print(request_json)

        ## Insert/Update Slave Details
        slave_row = slaves.query.filter(slaves.slave_hostname == request_json['system_info']['hostname']).order_by().first()
        if slave_row:
            slave_row.slave_last_connect = datetime.datetime.now()
            slave_row.test_id = request_json['test_id']
            slave_row.slave_cores = request_json['system_info']['cores']
            slave_row.slave_progressing = len(request_json['progressing_boxes'])
        else:
            slave_row = slaves(request_json['system_info']['hostname'], request_json['system_info']['version'], request_json['system_info']['system'], request_json['system_info']['cores'], request_json['system_info']['distribution'], request_json['system_info']['ip'], datetime.datetime.now(), len(request_json['progressing_boxes']))
            db.session.add(slave_row)
        db.session.commit()

        for key, progress_servers in request_json['progressing_boxes'].items():
            print(progress_servers)
            testroles_row = testroles.query.filter(testroles.id == progress_servers['id']).order_by(testroles.id).first()
            testroles_row.testrole_log = progress_servers['log']
            db.session.commit()

        for key, completed_servers in request_json['completed_boxes'].items():
            testroles_row = testroles.query.filter(testroles.id == completed_servers['id']).order_by(testroles.id).first()
            testroles_row.testrole_log = completed_servers['log']
            testroles_row.testrole_end_time = datetime.datetime.now()
            if (int(completed_servers['exit_code']) == 0):
                testroles_row.testrole_status = 2
            else:
                testroles_row.testrole_status = 3

            db.session.commit()

        available_processes = int(request_json['system_info']['cores']) - len(request_json['progressing_boxes'])

        print('Available Cores: ' + str(available_processes))

        data = {}
        data['completed_boxes'] = request_json['completed_boxes']
        data['status'] = 1

        test_row = tests.query.filter().order_by(tests.id.desc()).first()
        if test_row:
            data['test_id'] = test_row.id
        else:
            data['test_id'] = 0


        if int(request_json['call_type']) == 1:
            data['test_roles'] = []

            # Only do the next step if every alive slave has updated its test id

            alive_time = datetime.datetime.now() - datetime.timedelta(seconds=240)
            alive_slaves = slaves.query.filter(slaves.slave_last_connect > alive_time, slaves.test_id != data['test_id']).order_by().all()

            if len(alive_slaves) == 0:
                testrolesorder_row = testroles.query.filter(testroles.test_id == data['test_id'], testroles.testrole_status != 2).order_by(testroles.testrole_order).first()
                if testrolesorder_row:
                    testrole_order = testrolesorder_row.testrole_order
                    testroles_res = testroles.query.filter(testroles.test_id == data['test_id'], testroles.slave_id == 0, testroles.testrole_status == 0, testroles.testrole_order == testrole_order).order_by(testroles.id).limit(available_processes).all()
                    for testroles_row in testroles_res:
                        data['test_roles'].append({'id': testroles_row.id, 'name': testroles_row.testrole_name, 'type': testroles_row.testrole_type, 'ip': testroles_row.testrole_ipnum } )
                        testroles_row.slave_id = slave_row.id
                        testroles_row.testrole_start_time = datetime.datetime.now()
                        testroles_row.testrole_status = 1
                        db.session.commit()

                        # TODO: Assign slave_id to this node

        return Response(json.dumps(data),  mimetype='application/json')





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
