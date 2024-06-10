# -*- coding: utf-8 -*-
from django.contrib import admin
from oauth.models import Users, Department, Position
from django.contrib.auth.admin import UserAdmin
#from apps.customadmin.admin import CustomAdminSite


# @admin.register(Department)
# class DepartmentAdmin(admin.ModelAdmin):
#     """
#     部门展示类
#     """
#     ordering = ('id',)
#     list_display = (id, 'dep_name',)
#     search_fields = ('dep_name',)
#     list_filter = ('dep_name',)
#     list_per_page = 20


# @admin.register(Position)
# class PositionAdmin(admin.ModelAdmin):
#     """
#     职位展示类
#     """
#     ordering = ('id',)
#     list_display = (id, 'post_name',)
#     search_fields = ('post_name',)
#     list_filter = ('post_name',)
#     list_per_page = 20


@admin.register(Users)
class UsersAdmin(UserAdmin):
    """
    用户展示类
    """
    #model = Users
    list_display = ['username', 'name', 'gender', 'dep', 'post', 'birthday', 'mobile', 'email']
    search_fields = ('name', 'gender', 'dep', 'post',)
    list_filter = ( 'gender','dep',)
    list_per_page = 20

    # user 自定义字段
    fieldsets = UserAdmin.fieldsets + (
        ('个人详情', {'fields': ('name','gender','dep','mobile','birthday', )}),
    )

admin.site.site_header = '自动化测试1111111'
admin.site.site_title = '自动化测试2222'
admin.site.index_title = '自动化测3333'
