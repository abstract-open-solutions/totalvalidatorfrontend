# -*- encoding: utf-8 -*-
import uuid

from deform import ValidationFailure
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..forms import new_session_form
from ..models import ValidationSessionModel
from ..models import DBSession
from ..models import get_accessibility_validator_model
from ..models import get_markup_validator_model

from ..task import CrawlingTask

from .utils import base_view_params
from .utils import set_status_message
from .. import messageFactory as _


@view_config(route_name='new_session',
             renderer='templates/simple_form.pt',
             request_method="GET")
def new_session(request):
    form = new_session_form()
    params = base_view_params(request, _(u"New Session"), 'new_session').copy()
    params.update({
        'form': form.render()
    })

    return params


@view_config(route_name='new_session',
             renderer='templates/simple_form.pt',
             request_method="POST")
def new_session_action(request):
    form = new_session_form()
    params = base_view_params(request, _(u"New Session"), 'new_session').copy()
    params['form'] = form.render()

    controls = request.POST.items()
    try:
        data = form.validate(controls)
    except ValidationFailure, e:
        params['form'] = e.render()
        return params

    values = {
        'url': data['url'],
        'code': uuid.uuid4().hex,
        'status': 0,
        'limit': data['limit']
    }
    try:
        session = ValidationSessionModel(**values)
        DBSession.add(session)
        DBSession.flush()

        set_status_message(
            request,
            _(
                u"Added ${url} validation session",
                mapping={"url": values['url']}
            ),
            type_='success'
        )

        crawling = CrawlingTask()
        crawling.delay(session, data['limit'])

        # change session status
        session.status = 1

    except Exception, e:
        set_status_message(
            request,
            _(u"Error on create new validation session"),
            type_='danger'
        )
        return params

    url = request.route_url('home')
    return HTTPFound(location=url)
