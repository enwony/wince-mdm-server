#!/usr/bin/python

from flask import Flask, request, render_template
import re, types
import xml.etree.ElementTree as ET
import logging
from model import Device, Server, create_all
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASEURI = '/devicemgmt/server.aspx'

""" mobile py management server for windows ce devices. serve requests from clients """

app = Flask(__name__)
session = sessionmaker()
server = Server()

@app.context_processor
def utility_processor():
    def boolean(s):
        return ('true' if s else 'false')
    
    def interval(s):
        # TODO: can't find real information about this timediff format, does not count year
        i = int(s)
        secs = i % 60
        i = i / 60
        mins = i % 60
        i = i / 60
        hours = i % 24
        i = i / 24
        days = i % 30
        i = i / 30
        month = i / 12
        return "0000-{:02}-{:02} {:02}:{:02}:{:02}".format(month, days, hours, mins, secs)
    
    return dict(boolean=boolean, interval=interval)

def init_app():
    engine = create_engine('sqlite:///' + app.config['DATABASE'], convert_unicode=True)
    session.configure(bind = engine)
    create_all(engine)

def cut_namespace_request():
    """
        return parsed request data with cut-off namespace element
        additionally, added modified find method
    """
    def lookup(tree, path, default = ""):
        """
            try to find element and extract it text
            if not found, return default
        """
        find = tree.find('./' + path)
        if find is None: 
            return default
        else:
            return find.text.strip()
    
    xmlstring = re.sub(' xmlns="[^"]+"', '', request.data, count=1)
    result = ET.fromstring(xmlstring)
    result.lookup = types.MethodType(lookup, result) 
    return result


@app.route("/")
def identification():
    server = Server()
    return "{} {} is running and accessible via {}".format(server.title, server.version, BASEURI)

@app.route(BASEURI, methods = ['POST'])
def PollRequest():
    print('DUMP of REQUEST:[' + request.data + ']')
    db = session()
    tree = cut_namespace_request()
    device_id = tree.lookup('Identification/ID')
    
    if device_id == '':
        return "DeviceID not found", 500 
 
    # find/create and update parameters for device
    device = db.query(Device).get(device_id)
    if device == None:
        device = Device()
        device.id = device_id
        db.add(device)
    device.management_system = tree.lookup('ManagementSystem/Name')
    device.management_version = tree.lookup('ManagementSystem/Version')
    device.name = tree.lookup('Identification/DeviceName')
    device.username = tree.lookup('Identification/UserName')
    device.platform = tree.lookup('Identification/Platform')
    device.processor = tree.lookup('Identification/Processor')
    device.ip_address = tree.lookup('Identification/NetworkAdapter/IPAddress')
    device.ip_subnet = tree.lookup('Identification/NetworkAdapter/IPSubnet')
    device.codepage = tree.lookup('Identification/CodePage')
    device.default_locale_id = tree.lookup('Identification/SystemDefaultLCID')
    db.commit()
    
    response = render_template('poll_response.xml', device = device, server = Server())
    print('DUMP of RESPONSE: [' + response + ']')
    return response 
    
def InstructionRequest():
    pass

def PackageLocationRequest():
    pass

def FileCollectionReport():
    pass

def MachineInventoryReport():
    pass

def SoftwareInventoryReport():
    pass

def DownloadEventStatusReport():
    pass
        
