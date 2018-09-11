import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class Config(object):
	HOSTNAME = '127.0.0.1'
	PORT = '3306'
	DATABASE = 'flask_mov'
	USERNAME = 'root'
	PASSWORD = 'xzx199110'
	
	DB_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{database}".format(
		username=USERNAME,
		password=PASSWORD,
		host=HOSTNAME,
		port=PORT,
		database=DATABASE
	)
	
	SQLALCHEMY_DATABASE_URI = DB_URI
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	SECRET_KEY = 'xiao'
	DEBUG = True
	UP_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
		'static/uploads/'
	)
	FC_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
		'static/uploads/user/'
	)
