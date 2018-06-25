from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import AreaSerializer, SubAreaSerializer
from .models import Area
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None  # 行政区划不分页

    def get_queryset(self):
        """提供查询集"""
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()


    def get_serializer_class(self):
        """提供序列化器"""
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer
