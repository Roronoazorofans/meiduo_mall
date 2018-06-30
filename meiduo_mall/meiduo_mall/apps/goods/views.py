from django.shortcuts import render
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.generics import ListAPIView
from .serializers import SKUSerializer, SKUIndexSerializer
from rest_framework.filters import OrderingFilter
from .models import SKU
# Create your views here.


class SKUListView(ListAPIView):

    serializer_class = SKUSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return SKU.objects.filter(category_id=category_id, is_launched=True)


class SKUSearchViewSet(HaystackViewSet):
    """创建商品SKU搜索视图"""

    index_models = [SKU]
    serializer_class = SKUIndexSerializer
