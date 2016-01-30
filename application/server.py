from application import *
from flask import Flask, render_template, request, abort, redirect, url_for, flash, Response, jsonify, get_flashed_messages, session
from application.poll import *

@app.route('/')
def index():
    set_log('aa')
    return get_log()

@app.route('/cores')
def cores():
    return str(get_cores())
