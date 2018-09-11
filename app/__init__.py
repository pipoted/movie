from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()


def create_app():
	app = Flask(__name__)
	app.config.from_object(Config)
	db.init_app(app)
	
	app.debug = True
	
	from .admin import admin as admin_blueprint
	from .home import home as home_blueprint
	
	app.register_blueprint(admin_blueprint, url_prefix='/admin')
	app.register_blueprint(home_blueprint)
	
	# 404页面的配置
	@app.errorhandler(404)
	def page_not_found(error):
		return render_template('home/404.html'), 404
	
	return app

# # 创建app与db对象
# app = Flask(__name__)
# # 配置信息
# app.config.from_object(Config)
# db = SQLAlchemy()
# db.init_app(app)
# # 注册蓝图
# app.register_blueprint(admin_blueprint)
# app.register_blueprint(home_blueprint)
#
# print('app创建成功', app.debug)
