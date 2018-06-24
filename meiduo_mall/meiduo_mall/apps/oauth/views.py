from django.shortcuts import render
from rest_framework.settings import api_settings
from rest_framework.views import APIView,status
from oauth.serializers import OauthQQUserSerializer
from .utils import OauthQQ
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .exceptions import QQAPIError
from .models import OauthQQUser


# Create your views here.
class QQAuthURLView(APIView):
    """QQ登录逻辑第一步
    # 1.创建qq登录工具对象,
      2.传入next对应的回调的url网址
      3.返回响应数据　响应的url
    """
    def get(self, request):
        # 获取浏览器请求url中的next参数
        next = request.query_params.get('next')
        oauth = OauthQQ(state=next)
        login_url = oauth.get_qq_login_url()
        return Response({"login_url": login_url})

class QQAuthUserView(CreateAPIView):
    """校验、保存均在此序列化器中执行"""
    serializer_class = OauthQQUserSerializer

    def get(self, request):
        # 获取用户访问url中的code参数
        code = request.query_params.get('code')
        if not code:
            return Response({"message":"缺少code"},status=status.HTTP_400_BAD_REQUEST)
        # 创建访问qq服务器OauthQQ对象,使用code向qq服务器请求access_token
        oauth_qq = OauthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)
            open_id = oauth_qq.get_open_id(access_token)
        except QQAPIError:
            return Response({"message": "qq访问异常"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 根据用户的open_id查询用户是否绑定
        try:
            oauth_qq_user = OauthQQUser.objects.get(openid=open_id)
        except OauthQQUser.DoesNotExist:
            # 如果用户未绑定,创建本地access_token并返回给序列化器进行绑定
            access_token = oauth_qq.generate_bind_access_token(open_id)
            return Response({"access_token": access_token})
        else:
            # 如果用户已经绑定,则签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            user = oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            # 返回结果
            return Response({
                    'username': user.name,
                    'user_id': user.id,
                    'token': token
                    })


