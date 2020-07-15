"""
OpenID Adapter for Steam

The Steam login API is simple OpenID but requires extra API calls
for basic resources such as usernames.

Resources:

* Steam Web API Documentation
    https://steamcommunity.com/dev

* Steam Partner API documentation
    https://partner.steamgames.com/doc/features/auth#website
"""
from allauth.socialaccount import providers
from allauth.socialaccount.providers.openid.views import (
    OpenIDCallbackView,
    OpenIDLoginView,
)
from django.conf import settings
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from openid.consumer import consumer

from .provider import SteamCustomOpenIDProvider, extract_steam_id
import json

import os


STEAM_OPENID_URL = "https://steamcommunity.com/openid"

if os.environ.get('SC_SERVER') == 'dev':
    STEAM_REDIRECT_URL = getattr(
        settings, 'STEAM_REDIRECT_URL', 'http://127.0.0.1:8080')
else:
    STEAM_REDIRECT_URL = getattr(
        settings, 'STEAM_REDIRECT_URL', 'http://steamcomparer.com')


class SteamCustomOpenIDLoginView(OpenIDLoginView):
    provider = SteamCustomOpenIDProvider

    def get_form(self):
        items = dict(
            list(self.request.GET.items()) +
            list(self.request.POST.items())
        )
        items["openid"] = STEAM_OPENID_URL
        return self.form_class(items)

    def get_callback_url(self):
        return reverse(steam_callback)


class SteamCustomOpenIDCallbackView(OpenIDCallbackView):
    provider = SteamCustomOpenIDProvider

    def get(self, request):
        provider = self.provider(request)
        endpoint = request.GET.get('openid.op_endpoint', '')
        client = self.get_client(provider, endpoint)
        response = self.get_openid_response(client)
        steam_data = None

        if response.status == consumer.SUCCESS:
            steam_data = providers.registry \
                .by_id(self.provider.id, request)\
                .sociallogin_from_response(request, response)
        response = HttpResponseRedirect(STEAM_REDIRECT_URL)

        if steam_data:
            response.set_cookie('steam_data', str(steam_data))
        return response


steam_login = SteamCustomOpenIDLoginView.as_view()
steam_callback = SteamCustomOpenIDCallbackView.as_view()
