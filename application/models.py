from sqlalchemy import Column, Integer, String, DateTime
from application import db
from sqlalchemy.orm import relationship

class tests(db.Model):
    __tablename__ = 'tests'

    id = Column(Integer, primary_key=True)
    test_pushedat = Column(DateTime)

    def __init__(self, test_pushedat):
        self.test_pushedat = test_pushedat

class testroles(db.Model):
    __tablename__ = 'testroles'

    id = Column(Integer, primary_key=True)
    test_id = Column(Integer)
    testrole_name = Column(String(100))
    testrole_status = Column(Integer, default=0)
    testrole_start_time = Column(DateTime)
    testrole_end_time = Column(DateTime)
    testrole_log = Column(String, default='')
    testrole_order = Column(Integer, default=0)
    testrole_type = Column(Integer, default=0)
    testrole_ipnum = Column(Integer, default=0)
    slave_id = Column(Integer, default=0)

    def __init__(self, test_id, testrole_name, testrole_order, testrole_type, testrole_ipnum):
        self.test_id = test_id
        self.testrole_name = testrole_name
        self.testrole_order = testrole_order
        self.testrole_type = testrole_type
        self.testrole_ipnum = testrole_ipnum

class slaves(db.Model):
    __tablename__ = 'slaves'

    id = Column(Integer, primary_key=True)
    slave_hostname = Column(String(100), nullable=False)
    slave_version = Column(String(100), nullable=False)
    slave_system = Column(String(100), nullable=False)
    slave_cores = Column(Integer, nullable=False)
    slave_progressing = Column(Integer, nullable=False)
    slave_distribution = Column(String(100), nullable=False)
    slave_ip = Column(String(100), nullable=False)
    slave_last_connect = Column(DateTime)
    test_id =  Column(Integer)

    def __init__(self, slave_hostname, slave_version, slave_system, slave_cores, slave_distribution, slave_ip, slave_last_connect, slave_progressing):
        self.slave_hostname = slave_hostname
        self.slave_version = slave_version
        self.slave_system = slave_system
        self.slave_cores = slave_cores
        self.slave_distribution = slave_distribution
        self.slave_ip = slave_ip
        self.slave_last_connect = slave_last_connect
        self.slave_progressing = slave_progressing
