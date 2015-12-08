#!/usr/bin/python
from webapp import app, init_app

app.config['DATABASE'] = './database.db'
init_app()
app.run(host='0.0.0.0', port=80, debug=True)
