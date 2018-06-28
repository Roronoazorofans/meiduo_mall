# coding=utf-8
# 定义给用户签发JWT token
import re
from .models import User
from django.contrib.auth.backends import ModelBackend

def jwt_response_payload_handler(token, user=None, request=None):

    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }

# 增加用户名和手机号均可作为登录账号

def get_user_by_account(account):
    """根据传入的账号判断是用户名还是手机号
    :param account 可以是用户名也可以是手机号
    :return　user对象或者none

    """
    try:
        if re.match("^1[3-9]\d{9}$", account):
            # 根据手机号查询user对象
            user = User.objects.get(mobile=account)
        else:
            # 否则就是用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        # 返回user对象
        return user

# 自定义用户名和手机号认证
class UsernameMobileAuthBackend(ModelBackend):
    # 重写认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user