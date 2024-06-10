"""Salvation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework.authtoken import views
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls, ),
    #path('xadmin/', xadmin.site.urls),
    path('api-token-auth/', views.obtain_auth_token, name='auth-token'),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('oauth.urls')),
    path('testcases/', include('testcases.urls'),name = 'testcases'),
    #path('testcases/updateTmp1.html', views.update_tmp1_view, name='update_tmp1'),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


handler400 = 'oauth.views.error_views.bad_request'
handler403 = 'oauth.views.error_views.permission_denied'
handler404 = 'oauth.views.error_views.page_not_found'
handler500 = 'oauth.views.error_views.server_error'
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('/templates/',document_root = settings.TEMPLATES[0]['DIRS'][0])
