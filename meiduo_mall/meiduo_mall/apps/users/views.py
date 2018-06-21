from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView

from users.models import User
from users import serializers


# Create your views here.

class UsernameCountView(APIView):
    """判断账户是否存在"""
    # 获取指定用户名的数量，返回数据
    # 直接从用户表中获取,不必再通过使用序列化器

    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data = {
            "username": username,
            "count": count
        }

        return Response(data=data)



class MobileCountView(APIView):
    """判断手机号是否存在"""
    # 获取指定手机号的数量，返回数据
    # 直接从用户表中获取,不必再通过使用序列化器
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)

"""用户注册"""
class UserView(CreateAPIView):
    """验证手机号是否符合要求
        验证用户是否同意协议
        验证两次密码是否一致"""
    # 验证及注册交由序列化器完成
    serializer_class = serializers.CreateUserSerializer