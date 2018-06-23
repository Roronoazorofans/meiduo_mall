from django.shortcuts import render
from rest_framework.views import APIView
from .utils import OauthQQ
from rest_framework.response import Response

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
