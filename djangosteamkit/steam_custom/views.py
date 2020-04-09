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
from django.urls import reverse

from allauth.socialaccount.providers.openid.views import (
    OpenIDCallbackView,
    OpenIDLoginView,
)

from .provider import SteamOpenIDProvider, extract_steam_id
from openid.consumer import consumer
from django.shortcuts import HttpResponseRedirect
from django.conf import settings


STEAM_OPENID_URL = "https://steamcommunity.com/openid"
STEAM_REDIRECT_URL = getattr(settings, 'STEAM_REDIRECT_URL', 'http://127.0.0.1:8080')


class SteamOpenIDLoginView(OpenIDLoginView):
    provider = SteamOpenIDProvider

    def get_form(self):
        items = dict(
            list(self.request.GET.items()) +
            list(self.request.POST.items())
        )
        items["openid"] = STEAM_OPENID_URL
        return self.form_class(items)

    def get_callback_url(self):
        return reverse(steam_callback)


class SteamOpenIDCallbackView(OpenIDCallbackView):
    provider = SteamOpenIDProvider

    def get(self, request):
        provider = self.provider(request)
        endpoint = request.GET.get('openid.op_endpoint', '')
        client = self.get_client(provider, endpoint)
        response = self.get_openid_response(client)

        steamid = None
        if response.status == consumer.SUCCESS:
            steamid = extract_steam_id(request.GET.get('openid.identity', 'https://steamcommunity.com/openid/id/'))
        response = HttpResponseRedirect(STEAM_REDIRECT_URL)
        if steamid:
            response.set_cookie('steamid', steamid)
        return response


steam_login = SteamOpenIDLoginView.as_view()
steam_callback = SteamOpenIDCallbackView.as_view()
