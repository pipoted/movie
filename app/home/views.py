# coding=utf-8
import os
import uuid
from functools import wraps
from typing import Union

import werkzeug
from flask import (
	Blueprint, render_template, redirect, url_for,
	flash, request, session,
)
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, create_app
from app.home.forms import (
	RegistForm, LoginForm, UserDetailForm, UPPasswordForm, CommentForm,
)
from app.models import (
	User, UserLog, Preview,
	Movie, Tag, Comment, MovieCol,
)
from app.admin.views import change_filename

home = Blueprint(name='home', import_name=__name__)


# 登录时对用户名邮箱以及手机号进行唯一性检查
def validate(field: RegistForm):
	name = field.data['name']
	phone = field.data['phone']
	email = field.data['email']
	if User.query.filter_by(name=name).count() is 1:
		return '用户名已存在'
	elif User.query.filter_by(email=email).count() is 1:
		return '该邮箱已被注册'
	elif User.query.filter_by(phone=phone).count() is 1:
		return '该手机号已被注册'
	return ''


# 修改用户信息时对用户名邮箱以及手机号进行唯一性检查
def validate_session(field: RegistForm, user_field: User):
	name = field.data['name']
	phone = field.data['phone']
	email = field.data['email']
	if User.query.filter_by(
			name=name).count() is 1 and user_field.name != name:
		return '用户名已存在'
	elif User.query.filter_by(
			email=email).count() is 1 and user_field.email != email:
		return '该邮箱已被注册'
	elif User.query.filter_by(
			phone=phone).count() is 1 and user_field.phone != phone:
		return '该手机号已被注册'
	return ''


# 密码验证
# noinspection PyBroadException
def check_pwd(field: RegistForm):
	try:
		name = field.data['name']
	except:
		name = session['user']
	if User.query.filter_by(name=name).first() is None:
		return False
	else:
		return check_password_hash(
			User.query.filter_by(name=name).first().password,
			field.data['password'],
		)


# 定义验证是否登录的装饰器
def user_login_req(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'user' not in session or session['user'] is None:
			# 验证失败跳转到后台登录页面, 并提取该将要跳转地址的url
			return redirect(url_for('home.login', next=request.url))
		else:
			# 验证成功返回装饰函数
			return func(*args, **kwargs)
	
	return wrapper


# 登录界面
@home.route('/login/', methods=['GET', 'POST'])
def login() -> Union[str, None, werkzeug.wrappers.Response]:
	form = LoginForm()
	if request.method == 'GET':
		return render_template('home/login.html', form=form)
	else:
		if form.validate_on_submit() is True:  # 验证格式
			data = form.data
			user_field = User.query.filter_by(name=data['name']).first()
			if check_pwd(form) is True:  # 验证密码
				session.update({
					'user': user_field.name,
					'user_id': user_field.id
				})
				# 储存用户登录日志信息
				user_log = UserLog(
					user_id=user_field.id,
					ip=request.remote_addr,
				)
				db.session.add(user_log)
				db.session.commit()
				return redirect(
					request.args.get('next') or url_for('home.user'))
			else:
				flash('密码验证失败', 'err')
		else:
			flash('用户名或密码格式不正确', 'err')
		return redirect(url_for('home.login'))


# 退出登录,并删除session信息
@home.route('/logout/')
def logout() -> werkzeug.wrappers.Response:
	session.pop('user', None)
	session.pop('user_id', None)
	return redirect(url_for('home.login'))


# 会员注册界面
@home.route('/regist/', methods=['GET', 'POST'])
def regist():
	form = RegistForm()
	if form.validate_on_submit() is True:
		if validate(form) is not '':
			flash(validate(form), 'err')
		else:
			try:
				data = form.data
				field_user = User(
					name=data['name'],
					email=data['email'],
					phone=data['phone'],
					password=generate_password_hash(data['password']),
					uuid=uuid.uuid4().hex
				)
				db.session.add(field_user)
				db.session.commit()
				flash('注册成功', 'ok')
			except:
				raise flash('数据库存储异常', 'err')
	return render_template('home/regist.html', form=form)


# 会员中心界面,以及修改详细信息界面
@home.route('/user/', methods=['GET', 'POST'])
@user_login_req
def user() -> Union[str, None, werkzeug.wrappers.Response]:
	form = UserDetailForm()
	user_field = User.query.get(int(session['user_id']))
	
	if request.method == 'GET':  # 用户访问该页面时,各种属性的默认值
		form.face.validators = []
		form.name.data = user_field.name
		form.email.data = user_field.email
		form.phone.data = user_field.phone
		form.info.data = user_field.info
	
	if form.validate_on_submit() is True:
		data = form.data
		
		# 对name,phone,email进行唯一性检查
		if validate_session(form, user_field) is not '':
			flash(validate_session(form, user_field), 'err')
			return redirect(url_for('home.user'))
		else:  # 如果没有修改头像,那么头像默认为原来的
			if form.face.data.filename is '':
				form.face.data.filename = user_field.face
				face = user_field.face
			else:
				# 将上传的头像文件保存到本地
				path = create_app().config['FC_DIR']
				if os.path.exists(path) is False:
					os.makedirs(path)  # 当保存路径不存在时进行创建 √
				face = change_filename(form.face.data.filename)
				form.face.data.save(path + face)
			
			user_field.name = data['name']
			user_field.email = data['email']
			user_field.phone = data['phone']
			user_field.face = face
			user_field.info = data['info']
			
			db.session.add(user_field)
			db.session.commit()
			flash('修改成功', 'ok')
			return redirect(url_for('home.user'))
	
	return render_template('home/user.html', form=form, user=user_field)


# 修改密码界面
@home.route('/pwd/', methods=['GET', 'POST'])
@user_login_req
def pwd():
	form = UPPasswordForm()
	if request.method == 'GET':
		return render_template('home/pwd.html', form=form)
	else:
		if form.validate_on_submit() is True:
			# 对旧密码的验证
			if check_pwd(form) is False:
				flash('密码验证失败!请重新输入!', 'err')
			else:
				user_field = User.query.filter_by(name=session['user']).first()
				user_field.password = generate_password_hash(
					form.re_password.data)
				
				db.session.add(user_field)
				db.session.commit()
				flash('密码修改成功!', 'ok')
		
		return redirect(url_for('home.pwd'))


# 评论列表
@home.route('/comments/<int:page>/')
@user_login_req
def comments(page=None):
	if page is None:
		page = 1
	page_data = Comment.query.join(User).filter(
		User.id == session['user_id']
	).order_by(
		Comment.add_time.desc()
	).paginate(page=page, per_page=15)
	return render_template('home/comments.html', page_data=page_data)


# 会员登录日志
@home.route('/loginlog/<int:page>/', methods=['GET'])
@user_login_req
def login_log(page=None):
	if page is None:
		page = 1
	
	user_log = UserLog.query.filter_by(
		user_id=int(session['user_id'])
	).order_by(
		UserLog.add_time.desc()
	).paginate(page=page, per_page=10)
	return render_template('home/login_log.html', user_log=user_log)


# 添加电影收藏
@home.route('/moviecol/add/', methods=['GET', 'POST'])
@user_login_req
def movie_col_add():
	import json
	
	user_id = request.args.get('user_id', '')
	movie_id = request.args.get('movie_id', '')
	
	data = {}
	movie_col_count = MovieCol.query.filter_by(
		user_id=int(user_id),
		movie_id=int(movie_id),
	).count()
	if movie_col_count is 1:
		data = dict(ok=0)
	
	if movie_col_count is 0:
		movie_col_field = MovieCol(
			user_id=int(user_id),
			movie_id=int(movie_id)
		)
		db.session.add(movie_col_field)
		db.session.commit()
		data = dict(ok=1)
	
	return json.dumps(data)


# 电影收藏界面
@home.route('/moviecol/<int:page>/')
@user_login_req
def movie_col(page=None):
	if page is None:
		page = 1
	
	page_data = MovieCol.query.join(Movie).join(User).filter(
		Movie.id == MovieCol.movie_id,
		User.id == session['user_id'],
	).order_by(
		MovieCol.add_time.desc()
	).paginate(page=page, per_page=15)
	return render_template('home/movie_col.html', page_data=page_data)


# 主页
@home.route('/<int:page>/')
def index(page=None):
	if page is None:
		page = 1
	
	page_data = Movie.query.order_by(
		Movie.add_time.desc()
	).paginate(page=1, per_page=10)
	return render_template('home/index.html', page_data=page_data)


# 上映预告
@home.route('/animation/')
def animation():
	# 首页的轮播图动画效果
	temp = []
	data = Preview.query.all()
	for value in enumerate(data, 0):
		temp.append(value)
	return render_template('home/animation.html', data=temp)


# 搜索结果界面
@home.route('/search/<int:page>/')
def search(page=None):
	if page is None:
		page = 1
	
	key = request.args.get('key', '')  # 接收关键字
	# 分页信息
	page_data = Movie.query.filter(
		Movie.title.ilike('%' + key + '%')
	).order_by(
		Movie.add_time.desc()
	).paginate(page=page, per_page=10)
	
	movie_count = Movie.query.filter(
		Movie.title.ilike('%' + key + '%')
	).count()
	return render_template('home/search.html', key=key, page_data=page_data,
		movie_count=movie_count)


# 电影详情界面
@home.route('/play/<int:id_field>/<int:page>/', methods=['GET', 'POST'])
def play(id_field=None, page=None):
	movie = Movie.query.join(Tag).filter(
		Tag.id == Movie.tag_id,
		Movie.id == int(id_field)
	).first_or_404()
	movie.play_num = movie.play_num + 1
	if page is None:
		page = 1
	comment_data = Comment.query.join(User).filter(
		User.id == Comment.user_id
	).filter(
		movie.id == Comment.movie_id
	).order_by(
		Comment.add_time.desc()
	).paginate(page=page, per_page=15)
	
	form = CommentForm()
	if 'user' in session:
		if form.validate_on_submit() is True:
			data = form.data
			comment = Comment(
				content=data['content'],
				movie_id=movie.id,
				user_id=session['user_id'],
			)
			db.session.add(comment)
			db.session.commit()
			id_field = movie.id
			movie.comment_num += 1
			db.session.add(movie)
			db.session.commit()
			flash('评论添加成功', 'ok')
			return redirect(url_for('home.play', id_field=id_field, page=1))
	return render_template('home/play.html', movie=movie, form=form,
		comment_data=comment_data)
