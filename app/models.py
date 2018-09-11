from datetime import datetime
# from flask_sqlalchemy import SQLAlchemy
from app import db, create_app


# 会员模型
class User(db.Model):
	__tablename__ = 'user'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	name = db.Column(db.String(20), unique=True)  # 昵称
	password = db.Column(db.String(100))  # 密码
	email = db.Column(db.String(100), unique=True)  # 邮箱
	phone = db.Column(db.String(11), unique=True)  # 手机号码
	info = db.Column(db.Text)  # 个性简介
	face = db.Column(db.String(255), unique=True)  # 头像
	add_time = db.Column(db.DateTime, index=True,
		default=datetime.now)  # 注册时间
	uuid = db.Column(db.String(255), unique=True)  # 唯一标识符
	
	# 外键关联
	user_logs = db.relationship('UserLog', backref='user')  # 会员日志的外键关联
	comments = db.relationship('Comment', backref='user')  # 评论的外键关联
	movie_cols = db.relationship('MovieCol', backref='user')  # 收藏的外键关联
	
	def __repr__(self):
		return '<User %s>' % self.name


# 会员登录日志
class UserLog(db.Model):
	__tablename__ = 'user_log'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	ip = db.Column(db.String(100))  # 登录IP
	# 登录时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属会员
	
	def __repr__(self):
		return '<UserLog %s>' % self.id


# 标签
class Tag(db.Model):
	__tablename__ = 'tag'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	name = db.Column(db.String(100), unique=True)  # 标题
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	# 外键关联
	movies = db.relationship('Movie', backref='rag')
	
	def __repr__(self):
		return '<Tag %s>' % self.name


# 电影
class Movie(db.Model):
	__tablename__ = 'movie'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	title = db.Column(db.String(255), unique=True)  # 标题
	url = db.Column(db.String(255), unique=True)  # url地址
	info = db.Column(db.Text)  # 简介
	logo = db.Column(db.String(255), unique=True)  # 封面
	star = db.Column(db.SmallInteger)  # 星级
	play_num = db.Column(db.BigInteger)  # 播放量
	comment_num = db.Column(db.BigInteger)  # 评论量
	area = db.Column(db.String(255))  # 上映地区
	release_time = db.Column(db.Date)  # 上映时间
	length = db.Column(db.String(100))  # 电影时长
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	# 外键
	tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))  # 所属标签
	# 外键关联
	comments = db.relationship('Comment', backref='movie')  # 电影评论的外键关联
	movie_cols = db.relationship('MovieCol', backref='movie')  # 收藏的外键关联
	
	def __repr__(self):
		return '<Movie %s>' % self.title


# 上映预告
class Preview(db.Model):
	__tablename__ = 'preview'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	title = db.Column(db.String(255), unique=True)  # 标题
	logo = db.Column(db.String(255), unique=True)  # 封面
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	def __repr__(self):
		return '<Preview %s>' % self.title


# 评论
class Comment(db.Model):
	__tablename__ = 'comment'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	content = db.Column(db.Text)  # 评论内容
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	# 外键
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
	
	def __repr__(self):
		return '<Comment %s>' % self.id


# 电影收藏
class MovieCol(db.Model):
	__tablename__ = 'movie_col'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	# 外键
	movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))  # 所属电影
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # 所属用户
	
	def __repr__(self):
		return '<MovieCol %s>' % self.id


# 权限
class Auth(db.Model):
	__tablename__ = 'auth'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 权限编号
	name = db.Column(db.String(100), unique=True)  # 权限名称
	url = db.Column(db.String(255), unique=True)  # 权限地址
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	def __repr__(self):
		return '<Auth %s>' % self.name


# 角色
class Role(db.Model):
	__tablename__ = 'role'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 角色编号
	name = db.Column(db.String(100), unique=True)  # 角色名称
	auths = db.Column(db.String(600))  # 权限列表
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	admins = db.relationship('Admin', backref='role')
	
	def __repr__(self):
		return '<Role %s>' % self.name


# 管理员
class Admin(db.Model):
	__tablename__ = 'admin'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	name = db.Column(db.String(20), unique=True)  # 昵称
	password = db.Column(db.String(100))  # 密码
	is_super = db.Column(db.SmallInteger)  # 是否是超级管理员,其中0为超级管理员
	# 添加时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	# 外键
	role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # 所属角色
	# 外键关联
	admin_logs = db.relationship('AdminLog', backref='admin')  # 登录日志的外键关联
	op_logs = db.relationship('OpLog', backref='admin')  # 管理员操作日志的外键关联
	
	def __repr__(self):
		return '<Admin %s>' % self.name
	
	def check_pwd(self, pwd):
		from werkzeug.security import check_password_hash
		
		return check_password_hash(self.password, pwd)


# 管理员登录日志
class AdminLog(db.Model):
	__tablename__ = 'admin_log'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	ip = db.Column(db.String(100))  # 登录IP
	# 登录时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
	
	def __repr__(self):
		return '<AdminLog %s>' % self.id


# 操作日志
class OpLog(db.Model):
	__tablename__ = 'op_log'
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 编号
	ip = db.Column(db.String(100))  # 登录IP
	reason = db.Column(db.String(600))  # 操作原因
	# 登录时间
	add_time = db.Column(db.DateTime, index=True, default=datetime.now)
	
	admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))  # 所属管理员
	
	def __repr__(self):
		return '<OpLog %s>' % self.id


if __name__ == '__main__':
	role = Role()
