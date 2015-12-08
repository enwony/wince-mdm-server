#!/usr/bin/python

from flask import Flask, request, render_template, redirect, url_for
import re, types
import xml.etree.ElementTree as ET
import logging
from model import Device, Server, InventoryItem, InventoryProperty, create_all
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_bootstrap import Bootstrap

from flask.ext.wtf import Form
from wtforms.fields import BooleanField

class DeviceEditForm(Form):
    hardware_report_enable = BooleanField('Enable hardware report')

BASEURI = '/devicemgmt/server.aspx'

""" mobile py management server for windows ce devices. serve requests from clients """

app = Flask(__name__)
Bootstrap(app)
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
    db = session()
    """ show current device list """ 
    server = Server()
    devices = db.query(Device).all() 
    return render_template('device_list.html', devices=devices, server=server)

@app.route("/device/<device_id>", methods=["GET", "POST"])
def device(device_id):
    db = session()
    device = db.query(Device).get(device_id)
    form = DeviceEditForm(csrf_enabled=False)
    if form.validate_on_submit():
        device.hardware_report_enable = form.hardware_report_enable.data
        db.commit()
        return redirect(url_for('device', device_id = device_id))
    form.hardware_report_enable.data = device.hardware_report_enable
    return render_template('device_edit.html', form=form, device=device)    


@app.route("/inventory/<device_id>")
def inventory(device_id):
    db = session()
    device = db.query(Device).get(device_id)
    return render_template('device_inventory.html', device=device)
    
@app.route(BASEURI, methods = ['POST'])
def debug_server_request():
    if app.config['DEBUG']:
        print('DUMP REQUEST HEADERS: [' + str(request.headers) + ']')
        print('DUMP REQUEST: [' + request.data + ']')

    result = server_request()
    
    if app.config['DEBUG']:
        print('DUMP RESPONSE: [' + result + ']')
    return result
    
def server_request():
    """
        handles all query to MDM server from devices
    """
    # device id is mandatory
    device_id = request.headers.get('X-Device-UUID')
    if device_id == None:
        return 'Device UUID not set in request', 400
    
    action = request.headers.get('X-Device-Action', '')
    if action == 'Poll':
        return PollRequest(device_id)
    
    if action == 'Report':
        report_type = request.headers.get('X-Device-Reporttype', '')
        if report_type == 'MachineInventory':
            return MachineInventoryReport(device_id)
        return 'Unknown X-Device-Reporttype: {}'.format(report_type)
    
    return 'Unknown X-Device-Action field: {}'.format(action)
    
def PollRequest(device_id):
    db = session()
    tree = cut_namespace_request()
    
    # create or update parameters for device
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
    device.last_poll_update()
    db.commit()

    # send current parameters back to device    
    return render_template('poll_response.xml', device = device, server = Server())
    
def InstructionRequest():
    pass

def PackageLocationRequest():
    pass

def FileCollectionReport():
    pass

def MachineInventoryReport(device_id):
    """ 
        Handles inventory report from device. Writes it to database (replaces prev is exists)
        HINT: only accept inventory reports if device not in database 
    """
    db = session()
    
    device = db.query(Device).get(device_id)
    
    # delete all prev values and items
    for item in db.query(InventoryItem).filter(InventoryItem.device == device_id):
        db.query(InventoryProperty).filter(InventoryProperty.item == item.id).delete()
    db.query(InventoryItem).filter(InventoryItem.device == device_id).delete()
    
    tree = ET.fromstring(request.data)
    for source_item in tree.findall('InventoryItem'):
        item = InventoryItem()
        item.device = device.id
        item.name = source_item.attrib['name']
        db.add(item)                          
        db.commit()   
        for source_property in source_item.findall('Property'):
            property = InventoryProperty()
            property.item = item.id
            property.name = source_property.attrib['name']
            property.value = source_property.text
            db.add(property)
    device.last_inventory_update()
    db.commit()
    
    return ''
     
def SoftwareInventoryReport():
    pass

def DownloadEventStatusReport():
    pass
        
