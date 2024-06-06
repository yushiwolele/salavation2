# -*- coding: utf-8 -*-


from django.shortcuts import render


def page_not_found(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response


def server_error(request, exception=None):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response


def permission_denied(request, exception=None):
    context = {}
    response = render(request, "errors/403.html", context=context)
    response.status_code = 403
    return response


def bad_request(request, exception=None):
    context = {}
    response = render(request, "errors/400.html", context=context)
    response.status_code = 400
    return response
