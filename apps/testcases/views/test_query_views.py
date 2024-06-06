# -*- coding: utf-8 -*-            
# @Author : libeijie
# @Time : 2024/1/29 14:57
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def test_query(request):
    return render(request, template_name='testcases/test_query.html')