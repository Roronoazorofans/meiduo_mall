from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from . import constants
# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    # 添加邮箱验证状态字段,　布尔类型,默认为False
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")
    USERNAME_FIELD = 'mobile'

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    """定义生成邮箱链接的方法,因为要用到用户的id和email,所以定义在User模型类中"""
    def generate_verify_email_url(self):
        # 生成验证邮箱的url
        serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    def check_verify_email_token(token):
        serializer = TJWSSerializer(settings.SECRET_KEY,expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            email = data.get('email')
            user_id = data.get('user_id')
            try:
                user = User.objects.get(id=user_id, email=email)
            except User.DoesNotExist:
                return None
            else:
                return user