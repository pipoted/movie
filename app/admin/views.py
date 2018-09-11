# encoding=utf-8
from flask import (
	Blueprint, render_template, redirect, url_for, flash, session, request,
	abort,
)
from flask_sqlalchemy import Pagination
from wtforms.validators import DataRequired

from app import db, create_app
from app.admin.forms import (
	LoginForm, TagForm, MovieForm, PreviewForm, PwdForm, AuthForm, RoleForm,
	AdminForm,
)
from app.models import (
	Admin, Tag, Movie, Preview, User, Comment, MovieCol, OpLog, UserLog,
	AdminLog, Auth, Role,
)
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import os, uuid, datetime

admin = Blueprint(name='admin', import_name=__name__, url_prefix='/admin')


# 上下文应用处理器
@admin.context_processor
def tpl_extra():
	data = dict(
		online_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	)
	return data


# 密码验证
def validate_old_pwd(form):
	password = form.old_form.data
	if password is None:
		password = ''
	name = session['admin']
	admin_field = Admin.query.filter_by(
		name=name
	).first()
	return admin_field.check_pwd(password)


# 将传入的文件名改成安全的文件名并变成绝对路径
def change_filename(filename):
	"""
	传入一个安全的文件名,并对其进行修改
	:param filename: 安全的文件名
	:type filename: str
	:return: 修改完成的文件名
	:rtype: str
	"""
	filename = secure_filename(filename)
	file_info = os.path.splitext(filename)  # 使用该方法将文件名的内容与后缀分开
	filename = datetime.datetime.now().strftime(
		'%Y%m%d%H%M%S') + str(uuid.uuid4().hex) + file_info[-1]
	
	return filename


# 定义验证是否登录的装饰器
def admin_login_req(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if 'admin' not in session or session['admin'] is None:
			# 验证失败跳转到后台登录页面, 并提取该将要跳转地址的url
			return redirect(url_for('admin.login', next=request.url))
		else:
			# 验证成功返回装饰函数
			return func(*args, **kwargs)
	
	return wrapper


# 权限控制装饰器
def admin_auth(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		admin_field = Admin.query.join(
			Role
		).filter(
			Role.id == Admin.role_id,
			Admin.id == session['admin_id']
		).first()
		auths = admin_field.role.auths
		auths = list(map(lambda v: int(v), auths.split(',')))
		auths_list = Auth.query.all()
		urls = [v.url for v in auths_list for val in auths if val == v.id]
		rule = request.url_rule
		if rule.rule not in urls:
			abort(404)
		
		return func(*args, **kwargs)
	
	return wrapper


# 后台主页
@admin.route('/')
@admin_login_req
def index():
	return render_template('admin/index.html')


# 后台登录界面
@admin.route('/login/', methods=['POST', 'GET'])
def login():
	form = LoginForm()
	if form.validate_on_submit() is True:  # 对传入数据进行格式验证
		data = form.data  # 获取传入表单数据
		admin_field = Admin.query.filter_by(name=data['account']).first()
		if admin_field.check_pwd(data['password']) is False:
			flash('密码验证失败!')
			return redirect(url_for('admin.login'))  # 密码验证失败重定向到登录界面
		
		session.update({
			'admin': data['account'],
			'pwd': data['password'],
			'admin_id': admin_field.id
		})
		
		admin_log = AdminLog(
			admin_id=admin_field.id,
			ip=request.remote_addr,
		)
		db.session.add(admin_log)
		db.session.commit()
		# 密码验证成功之后重定向到后台管理页面主页
		return redirect(request.args.get('next') or url_for('admin.index'))
	return render_template('admin/login.html', form=form)


# 登出功能的实现,重定向到后台登录界面
@admin.route('/logout/')
@admin_login_req
def logout():
	session.pop('admin', None)  # 删除当前用户登录的session信息
	session.pop('pwd', None)
	session.pop('admin_id', None)
	return redirect(url_for('admin.login'))


# 修改密码界面
@admin.route('/pwd/', methods=['POST', 'GET'])
@admin_login_req
def pwd():
	form = PwdForm()
	password = form.new_pwd.data
	
	if request.method == 'GET':
		return render_template('admin/pwd.html', form=form)
	
	else:
		if form.validate_on_submit() is True:
			if validate_old_pwd(form) is False:
				flash('密码验证失败!', 'err')
			else:
				admin_field = Admin.query.filter_by(
					name=session['admin']).first()
				admin_field.password = generate_password_hash(password)
				db.session.add(admin_field)
				db.session.commit()
				flash('修改密码成功!', 'ok')
				return redirect(url_for('admin.logout'))
		
		return redirect(url_for('admin.pwd'))


# 添加标签页面
@admin.route('/tag/add/', methods=['POST', 'GET'])
@admin_login_req
@admin_auth
def tag_add():
	form = TagForm()
	if form.validate_on_submit() is True:
		# 格式验证成功之后提取数据
		data = form.data
		# 验证该标签是否唯一
		tag = Tag.query.filter_by(name=data['name']).first()
		if tag is not None:
			flash('该标签名已经存在!', 'err')  # 第二个参数是将信息分类,err是目录
			return redirect(url_for('admin.tag_add'))  # 唯一性检查失败刷新页面
		else:  # 唯一性验证成功将数据存入数据库
			tag = Tag(
				name=data['name'],
			)
			db.session.add(tag)
			db.session.commit()
			flash('标签添加成功', 'ok')
			
			oplog = OpLog(  # 将操作内容保存到操作日志之中
				admin_id=session['admin_id'],
				ip=request.remote_addr,
				reason='添加标签%s' % data['name']
			)
			db.session.add(oplog)
			db.session.commit()
	# return redirect(url_for('admin.tag_add'))  # 添加成功刷新页面
	return render_template('admin/tag_add.html', form=form)


# 标签管理列表页面
@admin.route('/tag/list/<int:page>/', methods=['GET', ])
@admin_login_req
@admin_auth
def tag_list(page=1):
	page_data = Tag.query.order_by(
		Tag.add_time.desc()  # 按照添加时间进行排序
	).paginate(page=page, per_page=10)  # 分页,当前页码以及每一页显示的数据量
	print(type(page_data))
	
	return render_template('admin/tag_list.html', page_data=page_data)


# 从主键获取标签信息并将该信息删除
@admin.route('/tag/del/<int:id_field>/', methods=['GET', ])
@admin_login_req
@admin_auth
def tag_del(id_field=None):
	tag = Tag.query.filter_by(id=id_field).first_or_404()
	db.session.delete(tag)
	db.session.commit()
	flash('标签删除成功', 'ok')
	return redirect(url_for('admin.tag_list', page=1))


# 标签列表页面中的编辑标签功能的实现
@admin.route('/tag/edit/<int:id_field>/', methods=['POST', 'GET'])
@admin_login_req
@admin_auth
def tag_edit(id_field):
	form = TagForm()
	tag = Tag.query.get_or_404(id_field)  # 根据id得到标签信息,不存在该id跳转到404页面
	if form.validate_on_submit() is True:
		# 格式验证成功之后提取数据
		data = form.data
		# 验证该标签是否唯一
		tag_count = Tag.query.filter_by(name=data['name']).count()
		
		if tag.name is not data['name'] and tag_count is 1:
			flash('该标签名已经存在!', 'err')  # 第二个参数是将信息分类,err是目录
			return redirect(
				url_for('admin.tag_edit', id_field=id_field))  # 唯一性检查失败刷新页面
		else:  # 唯一性验证成功将数据存入数据库
			tag.name = data['name']
			db.session.add(tag)
			db.session.commit()
			flash('标签修改成功!', 'ok')
	
	# return redirect(url_for('admin.tag_add'))  # 添加成功刷新页面
	return render_template('admin/tag_edit.html', form=form, tag=tag)


# 添加电影界面
@admin.route('/movie/add/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def movie_add():
	"""
	电影添加页面, 这里的电影播放器能够正常使用
	"""
	form = MovieForm()
	form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
	
	if form.validate_on_submit() is True:
		data = form.data
		path = create_app().config['UP_DIR']
		
		if os.path.exists(path) is False:
			os.makedirs(path)  # 当保存路径不存在时进行创建 √
		
		url = change_filename(form.url.data.filename)
		logo = change_filename(form.logo.data.filename)
		
		form.url.data.save(path + url)
		form.logo.data.save(path + logo)
		
		movie = Movie(  # 能够将文件名成功保存到数据库中 √
			title=data['title'],
			url=url,
			info=data['info'],
			logo=logo,
			star=int(data['star']),
			play_num=0,
			comment_num=0,
			tag_id=int(data['tag_id']),
			area=data['area'],
			release_time=data['release_time'],
			length=data['length'],
		)
		db.session.add(movie)
		db.session.commit()
		flash('电影添加成功', 'ok')
		return redirect(url_for('admin.movie_add'))
	return render_template('admin/movie_add.html', form=form)


# 电影列表界面
@admin.route('/movie/list/<int:page>/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def movie_list(page=1):
	"""
	电影列表界面
	:param page: 页码,前端模板传来page参数,为默认值,
	:type page: int
	"""
	# 对分页数据进行处理,对tag进行外键关联
	page_date: Pagination = Movie.query.join(Tag).filter(
		Tag.id == Movie.tag_id  # 对Tag表进行过滤
	).order_by(
		Movie.add_time.desc()
	).paginate(page=page, per_page=10)
	
	print(page_date.items)
	
	return render_template('admin/movie_list.html', page_date=page_date)


# 删除电影界面
@admin.route('/movie/del/<movie_id>/', methods=['GET'])
@admin_login_req
@admin_auth
def movie_del(movie_id=None):
	movie = Movie.query.get_or_404(int(movie_id))  # 传入id的值删除
	db.session.delete(movie)
	db.session.commit()
	flash('删除电影成功', 'ok')
	return redirect(url_for('admin.movie_list', page=1))


# 编辑电影界面
@admin.route('/movie/edit/<int:movie_id>/', methods=['GET', 'POST'])
@admin_login_req
def movie_edit(movie_id=None):
	if movie_id is None:
		movie_id = 1
	
	form = MovieForm()
	form.tag_id.choices = [(v.id, v.name) for v in Tag.query.all()]
	
	form.url.validators = []
	form.logo.validators = []
	
	movie = Movie.query.get_or_404(int(movie_id))
	print('查询操作成功')
	if request.method == 'GET':  # 在修改前在修改栏里面显示原来的值作为默认值
		# --> fixme 不能在编辑页面中的默认编辑框中保存默认文件
		form.info.data = movie.info
		form.tag_id.data = movie.tag_id
		form.star.data = movie.star
	
	if form.validate_on_submit() is True:
		data = form.data
		
		# 对片名进行唯一性检查,如果已经存在该片名则返回错误信息返回编辑页面
		movie_count = Movie.query.filter_by(title=data['title']).count()
		if movie_count is not 0 and movie.title != data['title']:
			flash('该片名已经存在', 'err')
			return redirect(url_for('admin.movie_edit', movie_id=movie_id))
		
		movie.title = data['title']  # 修改
		movie.star = data['star']
		movie.info = data['info']
		movie.tag_id = data['tag_id']
		movie.area = data['area']
		movie.length = data['length']
		movie.release_time = data['release_time']
		
		# 将视频以及图片文件保存到本地
		path = create_app().config['UP_DIR']
		if os.path.exists(path) is False:
			os.makedirs(path)  # 当保存路径不存在时进行创建 √
		
		if form.url.data.filename is not '':
			movie.url = change_filename(form.url.data.filename)
			form.url.data.save(path + movie.url)
		
		if form.logo.data.filename is not '':
			movie.logo = change_filename(form.logo.data.filename)
			form.logo.data.save(path + movie.logo)
		
		# logo = change_filename(form.logo.data.filename)
		#
		# form.url.data.save(path + url)
		# form.logo.data.save(path + logo)
		
		db.session.add(movie)  # 保存属性名以及属性内容(str)
		db.session.commit()
		
		flash('修改成功', 'ok')
		return redirect(url_for('admin.movie_edit', movie_id=movie.id))
	return render_template('admin/movie_edit.html', form=form, movie=movie)


# 添加电影预告页面
@admin.route('/preview/add/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def preview_add():
	form = PreviewForm()
	form.logo.validators.append(DataRequired('请上传封面!'))
	if form.validate_on_submit() is True:
		data = form.data
		# 将文件保存到本地
		path = create_app().config['UP_DIR']
		if os.path.exists(path) is False:
			os.makedirs(path)  # 当保存路径不存在时进行创建 √
		
		if form.logo.data.filename is not '':
			logo = change_filename(form.logo.data.filename)
			form.logo.data.save(path + logo)
			# 数据持久化
			preview = Preview(
				title=data['title'],
				logo=logo,
			)
			db.session.add(preview)
			db.session.commit()
			flash('操作成功', 'ok')
		else:
			flash('操作失败', 'err')
		
		return redirect(url_for('admin.preview_add'))
	return render_template('admin/preview_add.html', form=form)


# 电影的预告列表
@admin.route('/preview/list/<int:page>/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def preview_list(page=None):
	if page is None:
		page = 1
	
	page_date: Pagination = Preview.query.order_by(
		Preview.add_time.desc()
	).paginate(page=page, per_page=10)
	
	return render_template('admin/preview_list.html', page_date=page_date)


# 预告删除操作
@admin.route('/preview/del/<int:id_field>/', methods=['GET'])
@admin_login_req
@admin_auth
def preview_del(id_field=None):
	if id_field is None:
		id_field = 1
	
	preview = Preview.query.get_or_404(int(id_field))  # 传入id的值删除
	db.session.delete(preview)
	db.session.commit()
	flash('删除电影成功', 'ok')
	return redirect(url_for('admin.preview_list', page=1))


# 预告编辑页面
@admin.route('/preview/edit/<int:id_field>/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def preview_edit(id_field=None):
	if id_field is None:
		id_field = 1
	
	form = PreviewForm()
	# form.logo.validators = []
	preview = Preview.query.get_or_404(int(id_field))
	if request.method == 'GET':
		form.title.data = preview.title
	
	if form.validate_on_submit() is True:
		data = form.data
		form.logo.data.filename = preview.logo
		preview.title = data['title']
		path = create_app().config['UP_DIR']
		if os.path.exists(path) is False:
			os.makedirs(path)  # 当保存路径不存在时进行创建 √
		
		# 当用户没有修改logo属性时,不对logo进行保存操作
		if form.logo.data.filename is not '':
			preview.logo = change_filename(form.logo.data.filename)
			form.logo.data.save(path + preview.logo)
		
		db.session.add(preview)
		db.session.commit()
		flash('电影预告修改成功', 'ok')
	return render_template('admin/preview_edit.html', form=form,
		preview=preview, id_field=id_field)


# 会员管理列表
@admin.route('/user/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def user_list(page=None):
	if page is None:
		page = 1
	
	page_data = User.query.order_by(
		User.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/user_list.html', page_data=page_data)


# 查看用户详情
@admin.route('/user/view/<int:id_field>/')
@admin_login_req
@admin_auth
def user_view(id_field=None):
	if id_field is None:
		id_field = 1
	
	user = User.query.get_or_404(int(id_field))
	return render_template('admin/user_view.html', user=user)


# 删除该用户
@admin.route('/user/del/<int:id_field>/', methods=['GET'])
@admin_login_req
@admin_auth
def user_del(id_field=None):
	user = User.query.get_or_404(int(id_field))
	db.session.delete(user)
	db.session.commit()
	flash('删除操作完成!', 'ok')
	return redirect(url_for('admin.user_list', page=1))


# 评论列表
@admin.route('/comment/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def comment_list(page):
	if page is None:
		page = 1
	
	# 关联外键,取出相应的数据
	page_data = Comment.query.join(
		Movie
	).join(
		User
	).filter(
		Movie.id == Comment.movie_id,
		User.id == Comment.user_id,
	).order_by(
		Comment.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/comment_list.html', page_data=page_data)


# 删除该评论
@admin.route('/comment/del/<int:id_field>/', methods=['GET'])
@admin_login_req
@admin_auth
def comment_del(id_field=None):
	comment = Comment.query.get_or_404(int(id_field))
	db.session.delete(comment)
	db.session.commit()
	flash('删除操作完成!', 'ok')
	return redirect(url_for('admin.comment_list', page=1))


# 查看电影收藏页面
@admin.route('/moviecol/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def movie_col_list(page=None):
	if page is None:
		page = 1
	
	# 关联外键,取出相应的数据
	page_data = MovieCol.query.join(
		Movie
	).join(
		User
	).filter(
		Movie.id == MovieCol.movie_id,
		User.id == MovieCol.user_id,
	).order_by(
		MovieCol.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/movie_col_list.html', page_data=page_data)


# 删除收藏功能
@admin.route('/movie_col/del/<int:id_field>/', methods=['GET'])
@admin_login_req
@admin_auth
def movie_col_del(id_field=None):
	movie_col = MovieCol.query.get_or_404(int(id_field))
	db.session.delete(movie_col)
	db.session.commit()
	flash('删除操作完成!', 'ok')
	return redirect(url_for('admin.movie_col_list', page=1))


# 操作日志界面
@admin.route('/oplog/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def op_log_list(page=None):
	if page is None:
		page = 1
	
	page_data = OpLog.query.join(
		Admin
	).filter(
		Admin.id == OpLog.admin_id,
	).order_by(
		OpLog.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/op_log_list.html', page_data=page_data)


# 管理员登录日志
@admin.route('/adminloginlog/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def admin_login_log_list(page=None):
	if page is None:
		page = 1
	
	page_data = AdminLog.query.join(
		Admin,
	).filter(
		Admin.id == AdminLog.admin_id,
	).order_by(
		AdminLog.add_time.desc()
	).paginate(page=page, per_page=10)
	return render_template('admin/admin_login_log_list.html',
		page_data=page_data)


# 会员登录日志
@admin.route('/userloginlog/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def user_login_log_list(page=None):
	if page is None:
		page = 1
	
	page_data = UserLog.query.join(
		User
	).filter(
		User.id == UserLog.user_id,
	).order_by(
		UserLog.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/user_login_log_list.html',
		page_data=page_data)


# 添加角色页面
@admin.route('/role/add/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def role_add():
	form = RoleForm()
	form.auths.choices = [(v.id, v.name) for v in Auth.query.all()]
	
	if form.validate_on_submit() is True:
		data = form.data
		
		role = Role(
			name=data['name'],
			auths=','.join(map(lambda v: str(v), data['auths'])),
		)
		db.session.add(role)
		db.session.commit()
		flash('添加角色成功', 'ok')
	
	return render_template('admin/role_add.html', form=form)


# 角色列表页面
@admin.route('/role/list/<int:page>/', methods=['GET', ])
@admin_login_req
@admin_auth
def role_list(page=None):
	if page is None:
		page = 1
	
	page_data = Role.query.order_by(
		Role.add_time.desc(),
	).paginate(page=page, per_page=10)
	return render_template('admin/role_list.html', page_data=page_data)


# 删除角色功能
@admin.route('/role/del/<int:id_field>/', methods=['GET', ])
@admin_login_req
@admin_auth
def role_del(id_field=None):
	role = Role.query.filter_by(id=id_field).first_or_404()
	db.session.delete(role)
	db.session.commit()
	flash('角色删除成功', 'ok')
	return redirect(url_for('admin.role_list', page=1))


# 编辑角色页面
@admin.route('/role/edit/<int:id_field>/', methods=['POST', 'GET'])
@admin_login_req
@admin_auth
def role_edit(id_field):
	form = RoleForm()
	form.auths.choices = [(v.id, v.name) for v in Auth.query.all()]
	role = Role.query.get_or_404(id_field)
	if request.method == 'GET':
		form.auths.data = list(map(lambda v: int(v), role.auths.split(',')))
	if form.validate_on_submit() is True:
		data = form.data
		role.auths = ','.join(map(lambda v: str(v), data['auths']))
		role.name = data['name']
		db.session.add(role)
		db.session.commit()
		flash('角色修改成功!', 'ok')
	
	return render_template('admin/role_edit.html', form=form, role=role)


# 添加权限页面
@admin.route('/auth/add/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def auth_add():
	form = AuthForm()
	if form.validate_on_submit() is True:
		data = form.data
		auth = Auth(
			name=data['name'],
			url=data['url'],
		)
		db.session.add(auth)
		db.session.commit()
		flash('添加权限成功!', 'ok')
	
	return render_template('admin/auth_add.html', form=form)


# 权限管理列表页面
@admin.route('/auth/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def auth_list(page=None):
	if page is None:
		page = 1
	
	page_data = Auth.query.order_by(
		Auth.add_time.desc()  # 按照添加时间进行排序
	).paginate(page=page, per_page=10)  # 分页,当前页码以及每一页显示的数据量
	
	return render_template('admin/auth_list.html', page_data=page_data)


# 权限列表页面中的编辑标签功能的实现
@admin.route('/auth/edit/<int:id_field>/', methods=['POST', 'GET'])
@admin_login_req
@admin_auth
def auth_edit(id_field):
	form = AuthForm()
	auth = Auth.query.get_or_404(id_field)  # 根据id得到标签信息,不存在该id跳转到404页面
	if form.validate_on_submit() is True:
		data = form.data
		auth_count = Tag.query.filter_by(name=data['name']).count()
		
		if auth.name is not data['name'] and auth_count is 1:
			flash('该权限名已经存在!', 'err')  # 第二个参数是将信息分类,err是目录
			return redirect(
				url_for('admin.tag_edit', id_field=id_field))  # 唯一性检查失败刷新页面
		else:  # 唯一性验证成功将数据存入数据库
			auth.name = data['name']
			auth.url = data['url']
			db.session.add(auth)
			db.session.commit()
			flash('权限修改成功!', 'ok')
	
	return render_template('admin/auth_edit.html', form=form, auth=auth)


# 从主键获取标签信息并将该信息删除
@admin.route('/auth/del/<int:id_field>/', methods=['GET', ])
@admin_login_req
@admin_auth
def auth_del(id_field=None):
	auth = Auth.query.filter_by(id=id_field).first_or_404()
	db.session.delete(auth)
	db.session.commit()
	flash('权限删除成功', 'ok')
	return redirect(url_for('admin.auth_list', page=1))


# 添加管理员
@admin.route('/admin/add/', methods=['GET', 'POST'])
@admin_login_req
@admin_auth
def admin_add():
	form = AdminForm()
	form.role_id.choices = [(v.id, v.name) for v in Role.query.all()]
	
	if form.validate_on_submit() is True:
		data = form.data
		admin_field: Admin = Admin(
			name=data['name'],
			password=generate_password_hash(data['password']),
			role_id=data['role_id'],
			is_super=1,
		)
		db.session.add(admin_field)
		db.session.commit()
		flash('管理员添加成功!', 'ok')
	
	return render_template('admin/admin_add.html', form=form)


# 管理员列表页面
@admin.route('/admin/list/<int:page>/', methods=['GET'])
@admin_login_req
@admin_auth
def admin_list(page=None):
	if page is None:
		page = 1
	
	page_data = Admin.query.join(
		Role
	).filter(
		Role.id == Admin.role_id,
	).order_by(
		Admin.add_time.desc()  # 按照添加时间进行排序
	).paginate(page=page, per_page=10)  # 分页,当前页码以及每一页显示的数据量
	return render_template('admin/admin_list.html', page_data=page_data)
