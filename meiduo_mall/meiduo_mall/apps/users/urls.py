# coding=utf-8
from django.conf.urls import url
from users import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    url(r'^users/$', views.UserView.as_view()),
    # 调用rest_framework_jwt　提供的签发JWT　token的视图函数,　
    # 在用户每次登录或注册时后端都会签发一个token给前端保存,　用以保存用户的登录状态
    url(r'^authorizations/$', obtain_jwt_token),
    url(r'^emails/$', views.EmailView.as_view()), # 设置邮箱

]