from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from goods.models import SKU
from .serializers import CartSerializer, CartSKUSerializer
import base64
import pickle

# Create your views here.

class CartView(APIView):

    """购物车视图
    """

    # 重写父类的用户验证方法, 使其在不在进入视图之前检查JWT
    def perform_authentication(self, request):

        pass

    def post(self, request):

        """添加购物车
        １.　检查用户是否登录
        ２.　登录状态下将购物车数据存入redis
        ３.　未登录状态下将购物车数据存入cookie
        """

        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 对请求的用户进行验证
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            pl = redis_conn.pipeline()
        #
            """
            用户购物车数据 hash类型
            cart_user_id:{
                sku_id: count,
                sku_id: count,
                ...
            }
            用户勾选记录 set类型
            cart_selected_user_id:{
                sku_id, sku_id, ...
            }

            """
            # 记录购物车商品数量
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录勾选记录
            if selected:
                pl.sadd('cart_selected_%s' % user.id, sku_id)
            pl.execute()

            return Response(data=serializer.data)

        else:
            """用户未登录,存入cookie"""
            cart_str = request.COOKIES.get('cart')
            if cart_str:
                # 将字符串类型编码为bytes类型　　b'zifuchaun'
                cart_str = cart_str.encode()
                # 在将bytes类型通过base64解码成bytes类型
                cart_bytes = base64.b64decode(cart_str)
                cart_dict = pickle.loads(cart_bytes)
            else:

                cart_dict = {}

            if sku_id in cart_dict:
                # 如果存在,数量追加,勾选覆盖
                cart_dict[sku_id]['count'] += count
                cart_dict[sku_id]['selected'] = selected

            else:
                # 如果不存在就创建新的字典
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': selected
                }
            # 将字典形式使用pickle转为字符串形式,　用法与json一致
            cart_str = pickle.dumps(cart_dict)
            # 使用base64编码对其进行加密,加密后为bytes二进制类型,　故要进行解码为字符串,此处默认使用utf-8解码
            cart_cookie = base64.b64encode(cart_str).decode()

            response = Response(serializer.data)
            # 设置cookie  因为cookie为临时数据,设置max_age延长有效期
            response.set_cookie('cart',cart_cookie,max_age=constants.CART_COOKIE_EXPIRES)

            return response
                
    def get(self,request):
        """查询购物车
        判断用户是否已登录
        如果登录　　从redis中获取购物车数据
        未登录　　　从cookie中获取
        再从数据库中获取相应的商品sku信息
        """
        try:
            user = request.user
        except Exception:
            user = None
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            # 取出hash中的购物车数据
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            # redis_cart = {
            #     商品sku_id  bytes字节类型:  商品数量  bytes字节类型
            #     商品sku_id  bytes字节类型:  商品数量  bytes字节类型
            # ...
            # }
            # 获取set中勾选商品数据
            redis_cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)
            # 构建字典存储购物车中每个商品的数量和勾选状态
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_cart_selected
                }
        else:
            # 如果用户未登录,则从cookie中获取购物车信息
            cookie_cart = request.COOKIES.get('cart')
            if cookie_cart:
                # 将字符串类型编码为bytes类型　　b'zifuchaun'
                cookie_cart_str = cookie_cart.encode()
                # 在将bytes类型通过base64解码成bytes类型
                cookie_cart_bytes = base64.b64decode(cookie_cart_str)
                cart_dict = pickle.loads(cookie_cart_bytes)
            else:

                cart_dict = {}
        # 将cart_dict字典中的sku_id取出形成列表，再从数据库中取出相应的商品SKU信息
        sku_id_list = cart_dict.keys()
        # 取出相应的商品对象列表
        sku_obj_list = SKU.objects.filter(id__in=sku_id_list)
        for sku in sku_obj_list:
            # 向sku对象中添加属性　count 和　selected
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        serializer = CartSKUSerializer(instance=sku_obj_list,many=True)
        return Response(serializer.data)















