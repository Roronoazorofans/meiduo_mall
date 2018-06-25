# coding=utf-8
import logging
from django.core.mail import send_mail
from django.conf import settings

from celery_tasks.main import app
from .utils.yuntongxun.sms import CCP

logger = logging.getLogger("django")

# 验证码短信模板
SMS_CODE_TEMP_ID = 1

@app.task(name='send_sms_code')
def send_sms_code(mobile, code, expires):
    """
    发送短信验证码
    :param mobile: 手机号
    :param code: 验证码
    :param expires: 有效期
    :return: None
    """

    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [code, expires], SMS_CODE_TEMP_ID)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)



# 补充发送邮件的异步任务
@app.task(name='send_verify_email')
def send_verify_email(to_email, verify_url):
    """
        发送验证邮箱邮件
        :param to_email: 收件人邮箱
        :param verify_url: 验证链接
        :return: None
        """
    subject = "美多商城邮箱验证"
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用美多商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)

    send_mail(subject,"",settings.EMAIL_FROM,[to_email],html_message=html_message)