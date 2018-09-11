# encoding=utf-8
import flask
from flask_wtf import FlaskForm
from wtforms import (
	StringField, PasswordField, SubmitField, FileField, TextAreaField,
	SelectField, SelectMultipleField,
)
from wtforms.validators import DataRequired, ValidationError, EqualTo
from app.models import Admin, Tag


class LoginForm(FlaskForm):
	"""
	管理员登录的表单
	"""
	# 账号的判定
	account = StringField(
		label='账号',  # 标签名
		validators=[
			DataRequired('账号不能为空!')
		],  # 判定条件,报错信息
		description='账号',  # 描述信息
		
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入账号!',
			# 'required': 'required',  # 必选项
			# class ="form-control" placeholder="请输入账号！" >
		}  # 附加选项
	)
	# 密码的判定
	password = PasswordField(
		label='密码',
		validators=[
			DataRequired('请输入密码!'),
		],
		description='密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入密码!',
			# 'required': 'required',  # 必选项
		}  # 附加选项
	)
	# 提交
	submit = SubmitField(
		label='登录',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
			# class ="btn btn-primary btn-block btn-flat"
		}
	)
	
	def validate_account(self, field):
		"""
		对账号信息进行验证
		:rtype: bool
		:param field: 从中提取账号的值
		:type field:
		"""
		account = field.data
		admin = Admin.query.filter_by(name=account).first()
		if admin is None:
			raise ValidationError('该账号不存在')
		print('用户名验证成功')


class TagForm(FlaskForm):
	# 标签名格式的判定
	name = StringField(
		label='名称',
		validators=[
			DataRequired('请输入标签名!')
		],
		description='标签',
		render_kw={
			# class="form-control" id="input_name" placeholder="请输入标签名称！
			'class': 'form-control',
			'id': 'input_name',
			'placeholder': '请输入标签名称!',
		}
	)
	
	# 提交按钮
	submit = SubmitField(
		label='编辑',
		render_kw={
			'class': 'btn btn-primary',
			# class ="btn btn-primary btn-block btn-flat"
		}
	)


class MovieForm(FlaskForm):
	title = StringField(  # 对电影名称格式的判定
		label='片名',
		validators=[
			DataRequired('请输入片名!')
		],
		description='片名',
		render_kw={
			'class': 'form-control',
			'id': 'input_title',
			'placeholder': '请输入片名!',
		}
	)
	
	url = FileField(
		label='文件',
		validators=[
			DataRequired('请上传文件!')
		],
		description='文件',
	)
	
	info = TextAreaField(
		label='简介',
		validators=[
			DataRequired('请输入简介!')
		],
		description='简介',
		render_kw={
			'class': 'form-control',
			'row': 10,
		}
	)
	
	logo = FileField(
		label='封面',
		validators=[
			DataRequired('请上传封面!')
		],
		description='封面',
	)
	
	tag_id = SelectField(
		label='标签',
		validators=[
			DataRequired('请选择标签!')
		],
		coerce=int,
		choices=[],
		description='标签',
		render_kw={
			'class': 'form-control',
			'row': 10,
		}
	)
	
	star = SelectField(
		label='星级',
		validators=[
			DataRequired('请选择星级!')
		],
		coerce=int,
		choices=[
			(1, '一星'),
			(2, '二星'),
			(3, '三星'),
			(4, '四星'),
			(5, '五星'),
		],
		description='星级',
		render_kw={
			'class': 'form-control',
			'row': 10,
		}
	)
	
	area = StringField(
		label='地区',
		validators=[
			DataRequired('请输入地区名!')
		],
		description='地区',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入地区!',
		}
	)
	
	length = StringField(
		label='时长',
		validators=[
			DataRequired('请输入电影时长!')
		],
		description='时长',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入电影时长!',
		}
	)
	
	release_time = StringField(
		label='上映时间',
		validators=[
			DataRequired('请选择上映时间!')
		],
		description='上映时间',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入上映时间!',
			'id': 'input_release_time',
		}
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


class PreviewForm(FlaskForm):
	# 预告表单
	title = StringField(
		label='预告标题',
		validators=[
			DataRequired('请输入预告标题!')
		],
		description='预告标题',
		render_kw={
			'class': 'form-control',
			'id': 'input_title',
			'placeholder': '请输入预告标题!',
		}
	)
	
	logo = FileField(
		label='封面',
		validators=[
			# DataRequired('请上传封面!')
		],
		description='封面',
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


class PwdForm(FlaskForm):
	old_form = PasswordField(
		label='旧密码',
		validators=[
			DataRequired('请输入旧密码!'),
		],
		description='旧密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入旧密码!',
			# 'required': 'required',  # 必选项
		}  # 附加选项
	)
	
	new_pwd = PasswordField(
		label='新密码',
		validators=[
			DataRequired('请输入新密码!'),
		],
		description='新密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入新密码!',
			# 'required': 'required',  # 必选项
		}  # 附加选项
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


class AuthForm(FlaskForm):
	name = StringField(
		label='权限名称',
		validators=[
			DataRequired('请输入权限名称!')
		],
		description='权限名称',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入权限名称!',
		}
	)
	
	url = StringField(
		label='权限地址',
		validators=[
			DataRequired('请输入权限地址!')
		],
		description='权限地址',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入权限地址!',
		}
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


class RoleForm(FlaskForm):
	name = StringField(
		label='角色名称',
		validators=[
			DataRequired('请输入角色名称!')
		],
		description='角色名称',
		render_kw={
			'class': 'form-control',
			'id': 'input_title',
			'placeholder': '请输入角色名称!',
		}
	)
	
	auths = SelectMultipleField(
		label='权限列表',
		validators=[
			DataRequired('请选择权限!')
		],
		coerce=int,
		description='权限列表',
		render_kw={
			'class': 'form-control',
		}
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


class AdminForm(FlaskForm):
	name = StringField(
		label='管理员名称',
		validators=[
			DataRequired('管理员名称不能为空!')
		],
		description='管理员名称',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入管理员名称',
		}
	)
	
	password = PasswordField(
		label='管理员密码',
		validators=[
			DataRequired('请输入管理员密码!'),
		],
		description='管理员密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入管理员密码!',
		}
	)
	
	re_password = PasswordField(
		label='管理员重复密码',
		validators=[
			DataRequired('请输入管理员重复密码!'),
			EqualTo('password', message='两次密码不一致!'),
		],
		description='管理员重复密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入管理员重复密码!',
		}
	)
	
	role_id = SelectField(
		label='所属角色',
		choices='',
		coerce=int,
		render_kw={
			'class': 'form-control',
		}
	)
	
	submit = SubmitField(
		label='提交',
		render_kw={
			'class': 'btn btn-primary btn-block btn-flat',
		}
	)


