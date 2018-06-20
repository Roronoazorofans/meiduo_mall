# coding=utf-8
from rest_framework import serializers
from django_redis import get_redis_connection


class ImageCodeCheckSerializer(serializers.Serializer):
    """定义图片验证码校验序列化器"""

    image_code_id = serializers.UUIDField()
    text = serializers.CharField(max_length=4, min_length=4)

    # 定义校验方法
    def validate(self, attrs):
        """校验"""
        # 接受参数
        image_code_id = attrs['image_code_id']
        text = attrs['text']
        # 从redis中查询真实的图片验证码
        redis_conn = get_redis_connection('verify_codes')
        real_image_code_text = redis_conn.get('img_%s' % image_code_id)
        if not real_image_code_text:
            raise serializers.ValidationError('图片验证码无效')

        # 删除图片验证码
        redis_conn.delete('img_%s' % image_code_id)

        # 校验图片验证码
        real_image_code_text = real_image_code_text.decode()
        if real_image_code_text.lower() != text:
            raise serializers.ValidationError('图片验证码输入错误')

        # 判断是否在60s内
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get("send_flag_%s" % mobile)
        if send_flag:
            raise serializers.ValidationError('请求次数过于频繁')

        # 返回校验参数
        return attrs