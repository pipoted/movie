# coding:utf8
from flask_wtf import FlaskForm
from wtforms.fields import (
	StringField, PasswordField, SubmitField, FileField, TextAreaField,
)
from wtforms.validators import (
	DataRequired, EqualTo, Email, Regexp,
)


class RegistForm(FlaskForm):
	name = StringField(
		label='昵称',
		validators=[
			DataRequired('昵称不能为空!')
		],
		description='昵称',
		
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入昵称!',
		}
	)
	
	password = PasswordField(
		label='密码',
		validators=[
			DataRequired('请输入密码!'),
		],
		description='密码',
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入密码!',
		}
	)
	
	re_password = PasswordField(
		label='确认密码',
		validators=[
			DataRequired('请再次输入密码!'),
			EqualTo('password', message='密码不匹配!'),
		],
		description='确认密码',
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请再次输入密码!',
		}
	)
	
	email = StringField(
		label='邮箱',
		validators=[
			DataRequired('请输入邮箱!'),
			Email('邮箱格式不正确!'),
		],
		description='邮箱',
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入邮箱!',
		}
	)
	
	phone = StringField(
		label='手机号',
		validators=[
			DataRequired('请输入手机号码!'),
			Regexp('1[3458]\\d{9}', message='手机号码格式不正确!')
		],
		description='手机号',
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入手机号!',
		}
	)
	
	submit = SubmitField(
		label='注册',
		render_kw={
			'class': 'btn btn-lg btn-success btn-block',
		}
	)


class LoginForm(FlaskForm):
	name = StringField(
		label='账号',
		validators=[
			DataRequired('账号不能为空!')
		],
		description='账号',
		
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入账号!',
		}
	)
	
	password = PasswordField(
		label='密码',
		validators=[
			DataRequired('请输入密码!'),
		],
		description='密码',
		render_kw={
			'class': 'form-control input-lg',
			'placeholder': '请输入密码!',
		}
	)
	
	submit = SubmitField(
		label='登录',
		render_kw={
			'class': 'btn btn-lg btn-primary btn-block',
		}
	)


class UserDetailForm(FlaskForm):
	name = StringField(
		label='昵称',
		validators=[
			DataRequired('昵称不能为空!')
		],
		description='昵称',
		
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入昵称!',
		}
	)
	
	email = StringField(
		label='邮箱',
		validators=[
			DataRequired('请输入邮箱!'),
			Email('邮箱格式不正确!'),
		],
		description='邮箱',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入邮箱!',
		}
	)
	
	phone = StringField(
		label='手机号',
		validators=[
			DataRequired('请输入手机号码!'),
			Regexp('1[3458]\\d{9}', message='手机号码格式不正确!')
		],
		description='手机号',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入手机号!',
		}
	)
	
	face = FileField(
		label='头像',
		validators=[
		],
		description='头像',
	)
	
	info = TextAreaField(
		label='简介',
		validators=[
		],
		description='简介',
		render_kw={
			'class': 'form-control',
			'rows': 10,
		}
	)
	
	submit = SubmitField(
		label='保存修改',
		render_kw={
			'class': 'btn btn-success',
		}
	)


class UPPasswordForm(FlaskForm):
	password = PasswordField(
		label='旧密码',
		validators=[
			DataRequired('请输入旧密码!'),
		],
		description='旧密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入旧密码!',
		}
	)
	
	re_password = PasswordField(
		label='新密码',
		validators=[
			DataRequired('请输入新密码!'),
		],
		description='新密码',
		render_kw={
			'class': 'form-control',
			'placeholder': '请输入新密码',
		}
	)
	
	submit = SubmitField(
		label='保存修改',
		render_kw={
			'class': 'btn btn-success',
		}
	)


class CommentForm(FlaskForm):
	content = TextAreaField(
		label='评论内容',
		validators=[
			DataRequired('请输入评论内容!')
		],
		description='评论内容',
		render_kw={
			'id': 'input-content',
			'style': "margin: 0px; width: 1075px; height: 128px;",
		}
	)
	
	submit = SubmitField(
		label='提交评论',
		render_kw={
			'class': "btn btn-success",
			'id': "btn-sub",
		}
	)
