import cloudinary
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'abcdqwert'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '1234'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'petshop_data'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

cloudinary.config(
        cloud_name = 'di53bdbjf',
        api_key = '517256683852343',
        api_secret = 'Y8_JBxk_9VxQ3L3wHcAoeZAt_vw'
)