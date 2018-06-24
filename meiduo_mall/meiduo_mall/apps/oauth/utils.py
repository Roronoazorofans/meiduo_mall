# coding=utf-8
"""创建qq登录的辅助工具类"""
from django.conf import settings
from urllib.parse import urlencode, parse_qs
from urllib.request import urlopen
import json
from meiduo_mall.utils.exceptions import logger
from oauth import constants
from .exceptions import QQAPIError
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData

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

    # 通过ＱＱ服务器返回给浏览器,浏览器又向服务器请求的url中携带的code向ＱＱ服务器请求access_token
    def get_access_token(self, code):

        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        # 拼接访问QQ服务器的url
        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        # 通过urlopen　在本地服务器内访问QQ服务器
        response = urlopen(url)
        # 读取返回的数据
        response_data = response.read().decode()
        """返回说明：
        如果成功返回，即可在返回包中获取到Access Token。 如：
        access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14"""
        # 因为返回的数据格式是如上的url中的形式,需要进行解析成列表形式
        data = parse_qs(response_data)
        # 获取access_token
        access_token = data.get('access_token', None)  # 如果取不到默认为None
        if not access_token:
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError

        return access_token[0]


    """获取到access_token后再凭借它向ＱＱ服务器请求用户在ＱＱ服务器的唯一身份标识openid"""
    def get_open_id(self, access_token):

        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        response = urlopen(url)
        response_data = response.read().decode()
        # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
        # 返回时数据格式为字典形式
        try:
            data = json.loads(response_data[10:-4])
        except Exception:
            data = parse_qs(response_data)
            logger.error('code=%s msg=%s' % (data.get('code'), data.get('msg')))
            raise QQAPIError
        open_id = data.get('openid')
        return open_id


    """查询用户在本地服务器是否绑定了本地access_token"""
    @staticmethod
    def check_bind_access_token(access_token):
        """使用itsdangerous模块校验是否绑定了access_token"""
        serializer = TJWSSerializer(settings.SECRECT_KEY, expires_in=constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        try:
            data = serializer.loads(access_token)
        except BadData:
            return None
        else:
            return data['open_id']


    """定义生成用户在本地的access_token"""
    def generate_bind_access_token(self, open_id):
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.BIND_USER_ACCESS_TOKEN_EXPIRES)
        # 将字典数据转换  转换后为bytes类型
        token = serializer.dumps({"open_id": open_id})
        return token.decode()








