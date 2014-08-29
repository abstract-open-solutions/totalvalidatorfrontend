# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from ..utils import get_validation_session

from .utils import base_view_params


@view_config(route_name='delete',
             renderer='templates/delete.pt',
             permission='delete')
def delete(request):
    session = get_validation_session(request.matchdict['code'])
    params = base_view_params(request, 'Delete {}'.format(session.url)).copy()
    return params
