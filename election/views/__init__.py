from flask import Flask

from views import mod

# Settings
app = Flask(__name__)
app.register_blueprint(mod)
