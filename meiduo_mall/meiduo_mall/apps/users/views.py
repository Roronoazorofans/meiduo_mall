from django_redis import get_redis_connection
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin,UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView, status
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from goods.serializers import SKUSerializer
from users import constants
from users import serializers
from users.models import User
from users.serializers import AddUserBrowsingHistorySerializer


# Create your views here.

class UsernameCountView(APIView):
    """判断账户是否存在"""
    # 获取指定用户名的数量，返回数据
    # 直接从用户表中获取,不必再通过使用序列化器

    def get(self,request,username):
        count = User.objects.filter(username=username).count()

        data = {
            "username": username,
            "count": count
        }

        return Response(data=data)



class MobileCountView(APIView):
    """判断手机号是否存在"""
    # 获取指定手机号的数量，返回数据
    # 直接从用户表中获取,不必再通过使用序列化器
    def get(self,request,mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "mobile": mobile,
            "count": count
        }
        return Response(data)

"""用户注册"""
class UserView(CreateAPIView):
    """验证手机号是否符合要求
        验证用户是否同意协议
        验证两次密码是否一致"""
    # 验证及注册交由序列化器完成
    serializer_class = serializers.CreateUserSerializer



class UserDetailView(RetrieveAPIView):

    # 指明使用的序列化器
    serializer_class = serializers.UserDetailSerializer
    # 指明可以访问该视图的权限为已经通过认证的用户,即登录之后
    permission_classes = [IsAuthenticated]

    # 调用该方获取该模型类对象
    def get_object(self):
        return self.request.user

class EmailView(UpdateAPIView):
    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self, *args, **kwargs):
        return self.request.user


class VerifyEmailView(APIView):
    """邮箱验证"""
    def get(self,request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})



"""添加用户地址管理视图"""
class AddressViewset(CreateModelMixin,UpdateModelMixin,GenericViewSet):

    serializer_class = serializers.UserAddressSerializer
    permission_classes = [IsAuthenticated]

    """用户地址新增和删改"""
    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self,request,*args,**kwargs):
        """查询用户的所有地址"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user

        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data
        })

    def create(self, request, *args, **kwargs):
        """新增用户地址"""
        # 判断用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上线'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request,*args,**kwargs)

    def destroy(self, request, *args, **kwargs):
        """处理删除用户地址"""
        address = self.get_object()
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """设置默认地址"""
        address = self.get_object()
        request.user.default_address = address
        request.user.save()

        return Response({'message':'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """修改地址标题"""
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


# 用户浏览记录
class UserBrowsingHistoryView(mixins.CreateModelMixin, GenericAPIView):

    serializer_class = AddUserBrowsingHistorySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """保存"""
        return self.create(request)

    def get(self, request):
        user_id = request.user.id
        redis_conn = get_redis_connection('history')
        history = redis_conn.lrange("history_%s" % user_id, 0, constants.USER_BROWSING_HISTORY_COUNTS_LIMIT)
        skus = []
        for sku_id in history:
            sku = SKU.objects.get(id=sku_id)
            skus.append(sku)

        serializer = SKUSerializer(skus,many=True)
        return Response(serializer.data)

















