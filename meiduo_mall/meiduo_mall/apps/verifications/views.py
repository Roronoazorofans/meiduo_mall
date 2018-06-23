import random
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from celery_tasks.sms import tasks
from meiduo_mall.libs.captcha.captcha import captcha
from verifications import constants
from . import serializers


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


class SMSCodeView(GenericAPIView):
    """短信验证码
    传入参数： mobile, image_code_id, text
    """
    # 创建序列化器
    serializer_class = serializers.ImageCodeCheckSerializer
    # 创建短信验证码
    def get(self, request, mobile):
        # 校验图片验证码,　是否在６０秒内　使用序列化器完成
        serializer = self.get_serializer(data= request.query_params)
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = "%06d" % random.randint(0, 999999)

        # 保存验证码真实值与发送记录
        redis_conn = get_redis_connection('verify_codes')
        # 为了减少频繁的与redis交互,　使用管道将所有操作收集起来,让管道执行命令
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code) # 存入短信验证码
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1) # 存入发送记录
        # 让管道执行上面的命令
        pl.execute()

        # 发送短信验证码  调用第三方云通讯平台
        # try:
        #     ccp = CCP()
        #     expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        #     result = ccp.send_template_sms(mobile, [sms_code, expires], constants.SMS_CODE_TEMP_ID)
        # except Exception as e:
        #     logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
        #     return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     if result == 0:
        #         logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        #         return Response({'message': 'ok'})
        #     else:
        #         logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
        #         return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        # 使用celery发送短信
        # 发送短信验证码
        print(sms_code)
        # sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)
        # tasks.send_sms_code.delay(mobile, sms_code, sms_code_expires)

        return Response({"message": "OK"})


