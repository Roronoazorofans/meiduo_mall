from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from users.models import User
from users import serializers
from users.serializers import UserDetailSerializer, EmailSerializer


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



class UserDetailView(RetrieveAPIView):

    # 指明使用的序列化器
    serializer_class = serializers.UserDetailSerializer
    # 指明可以访问该视图的权限为已经通过认证的用户,即登录之后
    permission_classes = [IsAuthenticated]

    # 调用该方获取该模型类对象
    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    """邮箱验证"""
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})



