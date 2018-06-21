# coding=utf-8
from rest_framework import serializers
import re
from .models import User
from django_redis import get_redis_connection


"""定义序列化器处理校验工作
        验证手机号是否符合要求
        验证用户是否同意协议
        验证两次密码是否一致
        验证短信验证码是否符合要求"""
class CreateUserSerializer(serializers.ModelSerializer):
    """创建用户序列化器"""

    password2 = serializers.CharField(label="确认密码", write_only=True)
    sms_code = serializers.CharField(label="短信验证码", write_only=True)
    allow = serializers.CharField(label="同意协议", write_only=True)

    # 关联数据库
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'sms_code', 'mobile', 'allow')
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
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

    def validated_mobile(self, value):
        """验证手机号"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError("手机号格式错误")
        # 如果验证通过返回值
        return value

    def validate_allow(self, value):
        """验证用户是否同意协议"""
        if value != 'true':
            raise serializers.ValidationError("请同意用户协议")
        return value

    def validate(self, data):
        """验证两次密码是否一致"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError("两次密码不一致")

        # 判断短信验证码
        redis_conn = get_redis_connection('verify_codes')
        mobile = data['mobile']
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if not real_sms_code:
            raise serializers.ValidationError('无效的短信验证码')
        if data['sms_code'] != real_sms_code.decode():
            raise serializers.ValidationError('短信验证码错误')

        return data

    """创建用户"""
    def create(self, validated_data):
        #　移除数据库中不必要的属性
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        # 调用父类的create方法
        user = super().create(validated_data)

        # 调用django的认证系统加密
        user.set_password(validated_data['password'])
        user.save()

        return user

