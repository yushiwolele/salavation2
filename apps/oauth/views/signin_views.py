# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import render
from oauth.forms import SignUpForm

class SignInView(LoginView):
    """
    登录视图
    """
    template_name = 'accounts/login.html'


class SignOutView(LogoutView):
    """
    登出视图
    """
    template_name = 'accounts/login.html'


class SignUpView(CreateView):
    """
    注册视图
    """

    template_name = 'accounts/register.html'
    form_class = SignUpForm
    success_url = reverse_lazy('login')

    def form_invalid(self, form):
        """
        验证失败时触发
        :param form:
        :return:
        """
        return self.render_to_response({'form': form, })

def login(request):
    expiration = datetime.now() + timedelta(days=1)  # 设置Cookie 1天过期
    if request.method == "POST":

        user_name = request.POST.get("username", "")
        pass_word = request.POST.get("password", "")
        # 设置cookie
        response = render(request, template_name='accounts/index.html', context={"username": user_name})
        response.set_cookie("username", user_name, expires=expiration)
        return response
    elif request.method == "GET":
        return render(request, template_name='accounts/login.html', context={})
