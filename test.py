#!/usr/bin/python

import unittest
import webapp
import tempfile
import os
from model import Device

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, webapp.app.config['DATABASE'] = tempfile.mkstemp()
        webapp.app.config['TESTING'] = True
        self.app = webapp.app.test_client()
        webapp.init_app()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(webapp.app.config['DATABASE'])
        
    def test_poll_request(self):
        response = self.app.post('/devicemgmt/server.aspx', data=open('test/poll_request_example').read())
        db = webapp.session()
        device = db.query(Device).get('26CB0000-1807-1211-1502-736874726968')
        assert device != None
        assert device.name == 'SHTRIH-LightPOS'
        s = open('ssss', 'wb')
        s.write(response.data)
        s.close()
        print response.data
        assert response.data == open('test/poll_reply_example').read()
        
    def test_inventory_report(self):
        # need pass headers
        pass

if __name__ == '__main__':
    unittest.main()