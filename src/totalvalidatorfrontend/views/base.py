# -*- encoding: utf-8 -*-
from deform import ValidationFailure
from pyramid.security import authenticated_userid
from pyramid.view import forbidden_view_config
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from repoze.who.api import get_api

from ..forms import login_form

from .utils import base_view_params
from .utils import set_status_message

from .. import messageFactory as _


@view_config(route_name='set_lang', permission='view')
def set_locale_cookie(request):
    if request.GET['lang']:
        language = request.GET['lang']
        response = Response()
        response.set_cookie(
            '_LOCALE_',
            value=language,
            max_age=31536000  # max_age = year
        )
    return HTTPFound(
        location=request.environ['HTTP_REFERER'],
        headers=response.headers
    )


@forbidden_view_config(renderer='templates/login.pt')
def forbidden(request):
    user = authenticated_userid(request)
    if user is not None:
        set_status_message(
            request,
            _(u"You are not authorized to view this page"),
            type_='danger'
        )

    url = request.route_url('login')
    if request.application_url != request.url.rstrip('/'):
        url += '?came_from={}'.format(request.url)
    return HTTPFound(location=url)


@view_config(route_name='login',
             renderer='templates/login.pt',
             permission='public')
def login(request):
    form = login_form(request)
    params = base_view_params(request, _(u"Login")).copy()
    params["form"] = form.render()

    controls = request.POST.items()
    if controls:
        who_api = get_api(request.environ)

        try:
            data = form.validate(controls)
        except ValidationFailure, e:
            params['form'] = e.render()
            return params

        # check and authenticate
        authenticated, headers = who_api.login(data)
        if authenticated:
            came_from = request.params.get('came_from', '/')

            return HTTPFound(
                location=came_from,
                headers=headers
            )
        else:
            set_status_message(
                request,
                _(u"Invalid username or password"),
                type_='danger'
            )
            return HTTPFound(
                location=login_url
            )
    return params


@view_config(route_name='logout', permission='view')
def logout(request):
    who_api = get_api(request.environ)
    headers = who_api.logout()

    set_status_message(
        request,
        _(u"Logged out"),
        type_='success'
    )

    return HTTPFound(location='/login', headers=headers)
