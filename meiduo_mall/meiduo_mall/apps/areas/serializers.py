# coding=utf-8
from rest_framework import serializers
from .models import Area


class AreaSerializer(serializers.ModelSerializer):
    """创建省级行政区划序列化器关联相应的数据库"""

    class Meta:
        model = Area
        fields = ('id', 'name')


class SubAreaSerializer(serializers.Serializer):
    """创建子行政区划序列化器"""
    subs = AreaSerializer(many=True, read_only=True)
    class Meta:
        model = Area
        fields = ('id', 'name', 'subs')