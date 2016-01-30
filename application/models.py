from sqlalchemy import Column, Integer, String, DateTime
from application import db
from sqlalchemy.orm import relationship

class testroles(db.Model):
    __tablename__ = 'testroles'

    id = Column(Integer, primary_key=True)
    testrole_name = Column(String(100), nullable=False)

    def __init__(self, testrole_name):
        self.testrole_name = testrole_name

class slaves(db.Model):
    __tablename__ = 'slaves'

    id = Column(Integer, primary_key=True)
    slave_hostname = Column(String(100), nullable=False)
    slave_version = Column(String(100), nullable=False)
    slave_system = Column(String(100), nullable=False)
    slave_cores = Column(String(100), nullable=False)
    slave_distribution = Column(String(100), nullable=False)
    slave_ip = Column(String(100), nullable=False)
    slave_last_connect = Column(DateTime)

    def __init__(self, slave_hostname, slave_version, slave_system, slave_cores, slave_distribution, slave_ip, slave_last_connect):
        self.slave_hostname = slave_hostname
        self.slave_version = slave_version
        self.slave_system = slave_system
        self.slave_cores = slave_cores
        self.slave_distribution = slave_distribution
        self.slave_ip = slave_ip
        self.slave_last_connect = slave_last_connect

class testhistory(db.Model):
    __tablename__ = 'testhistory'

    id = Column(Integer, primary_key=True)
    testrole_id = Column(Integer, nullable=False)
    testhistory_result = Column(Integer)
    testhistory_datime = Column(DateTime)
    testhistory_log = Column(String)

    def __init__(self, testrole_id, testhistory_result, testhistory_datime, testhistory_log):
        self.testrole_id = testrole_id
        self.testhistory_result = testhistory_result
        self.testhistory_datime = testhistory_datime
        self.testhistory_log = testhistory_log
