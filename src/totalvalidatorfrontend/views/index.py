# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from webhelpers import paginate
from ..models import DBSession
from ..models import ValidationSessionModel

from .utils import base_view_params
from .utils import get_errors
from .utils import get_n_pages
from .. import messageFactory as _

BATCH_SIZE = 20


@view_config(route_name='home',
             renderer='templates/index.pt',
             permission='view')
def index(request):
    query = DBSession.query(ValidationSessionModel)
    num_results = query.count()
    page_url = paginate.PageURL_WebOb(request)
    results = paginate.Page(
        query,
        page=int(request.params.get("page", 1)),
        items_per_page=BATCH_SIZE,
        url=page_url
    )
    pager = results.pager(
        curpage_attr={'class': 'active'}
    )

    # XXX: DEBUG
    # session = DBSession.query(
    #     ValidationSessionModel
    # ).filter(
    #     ValidationSessionModel.id == 1
    # ).one()
    # from ..utils import update_errors_totals
    # # import pdb; pdb.set_trace( )
    # update_errors_totals(session)

    params = base_view_params(request, _(u'Dashboard')).copy()
    params.update({
        'results': results,
        'num_results': num_results,
        'pager': pager,
        'get_errors': lambda x: get_errors(x),
        'get_n_pages': lambda x: get_n_pages(x)
    })

    return params
