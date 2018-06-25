# coding=utf-8
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from users.models import User
from .utils import OauthQQ
from django_redis import get_redis_connection
from .models import OauthQQUser



class OauthQQUserSerializer(serializers.ModelSerializer):
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    sms_code = serializers.CharField(label='短信验证码', write_only=True)
    access_token = serializers.CharField(label='操作凭证', write_only=True)
    token = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('mobile', 'password', 'sms_code', 'access_token', 'id', 'username', 'token')
        extra_kwargs = {
            'username': {
                'read_only': True
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate(self, attrs):
        # 校验access_token
        access_token = attrs['access_token']
        open_id = OauthQQ.check_bind_access_token(access_token)
        if not open_id:
            raise serializers.ValidationError("无效的access_token")
        attrs['open_id'] = open_id

        # 检验短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        # 通过手机号查询用户是否存在,如果用户存在,校验用户密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError("密码错误")
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        open_id = validated_data['open_id']
        user = validated_data['user']
        mobile = validated_data.get('mobile')
        password = validated_data['password']

        if not user:
            # 如果用户不存在，则创建用户用于绑定open_id
            user = User.objects.create_user(username=mobile,mobile=mobile, password=password)

        # 绑定user 和　open_id
        OauthQQUser.objects.create(user=user, openid=open_id)

        # 签发jwt token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        user.token = token
        return user








