from werkzeug.contrib.fixers import ProxyFix

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = ProxyFix(app.wsgi_app)

from app import views
