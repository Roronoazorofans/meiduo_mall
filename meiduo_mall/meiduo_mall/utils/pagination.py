# coding=utf-8
from rest_framework.pagination import PageNumberPagination

"""将分页配置到全局应用中,因为可能其他地方也可能使用到"""


class StandardResultsSetPagination(PageNumberPagination):

    # 默认每页显示条数
    page_size = 2
    # 指定前端可以通过什么参数修改每页显示的条数
    page_size_query_param = 'page_size'
    # 每页的最大显示量
    max_page_size = 20

