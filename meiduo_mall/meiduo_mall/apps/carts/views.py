from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts import constants
from .serializers import CartSerializer
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
            pl = redis_conn.pipline()
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

            return Response(serializer.data)

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
                
















