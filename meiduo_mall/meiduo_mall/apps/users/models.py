from django.db import models
from django.contrib.auth.models import AbstractUser
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer, BadData
from django.conf import settings
from . import constants
from meiduo_mall.utils.models import BaseModel
# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name="手机号")
    # 添加邮箱验证状态字段,　布尔类型,默认为False
    email_active = models.BooleanField(default=False, verbose_name="邮箱验证状态")
    default_address = models.ForeignKey('users.Address',on_delete=models.SET_NULL,related_name='users',null=True,blank=True,verbose_name='默认地址')
    # USERNAME_FIELD = 'mobile'

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


"""添加用户地址管理模型类"""
class Address(BaseModel):
    """
    :param
    user 用户
    title　地址名称
    receiver  收货人
    province  省
    city　市
    district 区
    place  地址
    mobile　手机
    tel 固定电话
    email 电子邮箱
    """
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses', verbose_name='用户')
    title = models.CharField(max_length=20, verbose_name='地址名称')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    province = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='province_addresses',verbose_name='省')
    city = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='city_addresses',verbose_name='市')
    district = models.ForeignKey('areas.Area',on_delete=models.PROTECT,related_name='district_addresses',verbose_name='区')
    place = models.CharField(max_length=30,verbose_name='地址')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    tel = models.CharField(max_length=20,null=True,blank=True,default='',verbose_name='固定电话')
    email = models.CharField(max_length=30,null=True,blank=True,default='',verbose_name='电子邮箱')
    is_deleted = models.BooleanField(default=False,verbose_name='逻辑删除')

    # 声明
    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = '用户地址'
        ordering = ['-update_time']


