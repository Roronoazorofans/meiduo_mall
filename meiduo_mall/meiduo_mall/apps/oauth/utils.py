# coding=utf-8
"""创建qq登录的辅助工具类"""
from django.conf import settings
from urllib.parse import urlencode

class OauthQQ(object):

    def __init__(self,client_id=None,client_secret=None,redirect_uri=None,state=None):
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE
    # 获取qq认证请求的url
    def get_qq_login_url(self):

        # 构造ｘ响应的url数据
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }
        # 注意需要将url进行URLEncode  params原本是字典,　要调用urlencode解码为url数据
        url = "https://graph.qq.com/oauth2.0/authorize?" + urlencode(params)
        # 返回浏览器需要访问的url　
        return url