# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""CAS login/logout replacement views"""

from urllib import urlencode
from urlparse import urljoin

from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib import messages
# MODIF NC LILLE
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

__all__ = ['login', 'logout']


def _service_url(request, redirect_to=None):
    """Generates application service URL for CAS"""

    protocol = ('http://', 'https://')[request.is_secure()]
    host = request.get_host()
    service = protocol + host + request.path
    if redirect_to:
        if '?' in service:
            service += '&'
        else:
            service += '?'
        service += urlencode({REDIRECT_FIELD_NAME: redirect_to})
        # if request.GET.get("is_iframe"):
        #    service += "&is_iframe=true"
    return service


def _redirect_url(request):
    """Redirects to referring page, or CAS_REDIRECT_URL if no referrer is
    set.
    """
    next = request.GET.get(REDIRECT_FIELD_NAME)
    if not next:
        if settings.CAS_IGNORE_REFERER:
            next = settings.CAS_REDIRECT_URL
        else:
            next = request.META.get('HTTP_REFERER', settings.CAS_REDIRECT_URL)
        prefix = (('http://', 'https://')[request.is_secure()] +
                  request.get_host())
        if next.startswith(prefix):
            next = next[len(prefix):]
    return next


def _login_url(service):
    """Generates CAS login URL"""

    params = {'service': service}
    if settings.CAS_EXTRA_LOGIN_PARAMS:
        params.update(settings.CAS_EXTRA_LOGIN_PARAMS)
    return urljoin(settings.CAS_SERVER_URL, 'login') + '?' + urlencode(params)


def _logout_url(request, next_page=None):
    """Generates CAS logout URL"""

    url = urljoin(settings.CAS_SERVER_URL, 'logout')
    if next_page:
        protocol = ('http://', 'https://')[request.is_secure()]
        host = request.get_host()
        # MODIF NC LILLE1
        #url += '?' + urlencode({'url': protocol + host + next_page})
        url += '?' + urlencode({'service': protocol + host + next_page})
    return url

from django.utils.http import urlquote


def login(request, next_page=None, required=False):
    """Forwards to CAS login URL or verifies CAS ticket"""
    if not next_page:
        next_page = _redirect_url(request)

    if request.user.is_authenticated():
        message = _(u'You are logged in as %s.') % request.user.username
        messages.success(request, message)
        return HttpResponseRedirect(next_page)

    ticket = request.GET.get('ticket')
    service = _service_url(request, next_page)
    if ticket:
        from django.contrib import auth
        user = auth.authenticate(
            ticket=ticket, service=service, request=request)
        if user is not None:
            auth.login(request, user)
            name = user.first_name or user.username
            message = _(
                u'Login succeeded. Welcome, %s.') % name.decode('utf-8')
            messages.success(request, message)
            return HttpResponseRedirect(next_page)
        elif settings.CAS_RETRY_LOGIN or required:
            return HttpResponseRedirect(_login_url(service))
        else:
            error = _("<h1>Forbidden</h1><p>Login failed.</p>")
            return HttpResponseForbidden(error)
    # MODIF NC LILLE1 AJOUT GATEWAY
    # else:
    #    return HttpResponseRedirect(_login_url(service))
    else:
        if not settings.CAS_EXTRA_LOGIN_PARAMS or settings.CAS_EXTRA_LOGIN_PARAMS == {}:
            if request.GET.get('gateway') and request.GET.get('gateway') == "False":
                return HttpResponseRedirect(_login_url(service))
            settings.CAS_EXTRA_LOGIN_PARAMS = {"gateway": True}
            return HttpResponseRedirect(_login_url(service))
        else:
            settings.CAS_EXTRA_LOGIN_PARAMS = {}
            if "is_iframe=true" in next_page:  # request.GET.get("is_iframe"):
                return HttpResponseRedirect(reverse('account_login') + "?gateway=False&is_iframe=true&next=" + urlquote(next_page))
            else:
                return HttpResponseRedirect(reverse('account_login') + "?gateway=False&next=" + urlquote(next_page))


def logout(request, next_page=None):
    """Redirects to CAS logout page"""

    from django.contrib.auth import logout
    logout(request)
    if not next_page:
        next_page = _redirect_url(request)
    if settings.CAS_LOGOUT_COMPLETELY:
        return HttpResponseRedirect(_logout_url(request, next_page))
    else:
        return HttpResponseRedirect(next_page)
