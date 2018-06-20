from django.shortcuts import render
from rest_framework.views import APIView
from verifications.utils.captcha.captcha import captcha
from django_redis import get_redis_connection
from verifications import constants
from django.http import HttpResponse

# Create your views here.
class ImageCodeView(APIView):
    """获取图片验证码"""
    def get(self, request, image_code_id):
        # 调用第三方函数产生图片验证码

        text, image = captcha.generate_captcha()
        # 链接redis数据库将image_code_id与图片验证码内容保存至redis数据库, 并设置过期时间
        redis_conn = get_redis_connection("verify_codes")  # type:
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES,text )

        # 返回图片数据
        return HttpResponse(image, content_type="images/jpg")
