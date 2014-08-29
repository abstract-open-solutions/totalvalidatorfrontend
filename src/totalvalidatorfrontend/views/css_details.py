# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from ..models import DBSession
from ..models import get_css_validator_model

from .utils import base_view_params
from .. import messageFactory as _


@view_config(route_name='css_url_details',
             renderer='templates/css_url_details.pt')
def css_url_details(request):
    code = request.matchdict['code']
    urlhash = request.matchdict['urlhash']

    CSSModel = get_css_validator_model(code)
    query = DBSession.query(CSSModel).filter(
        CSSModel.urlhash == urlhash
    ).order_by(CSSModel.type)

    if query.count() == 0:
        # TODO: complete
        raise Exception
    errors = {}
    url = None
    for row in query.filter(CSSModel.type == 'error'):
        if not url:
            url = row.url
        errorhash = row.errorhash
        if errorhash not in errors:
            errors[errorhash] = {
                'errorhash': errorhash,
                'total': 0,
                'error': row.error,
                'errortype': row.errortype,
                'references': []
            }
        error = errors[errorhash]
        error['total'] += 1
        error["references"].append({
            'position': "L {}".format(row.line),
            'source': row.source,
            'context': row.context,
            'type': row.type
        })

    warnings = {}
    for row in query.filter(CSSModel.type == 'warning'):
        errorhash = row.errorhash
        if errorhash not in warnings:
            warnings[errorhash] = {
                'errorhash': errorhash,
                'total': 0,
                'error': row.error,
                'errortype': row.errortype,
                'references': []
            }
        error = warnings[errorhash]
        error['total'] += 1
        error["references"].append({
            'position': "L {}".format(row.line),
            'source': row.source,
            'context': row.context,
            'type': row.type
        })

    title = _(u'CSS URL details')
    params = base_view_params(request, title).copy()
    params.update({
        "url": url,
        "errors": errors,
        "warnings": warnings,
        "code": code,
        "breadcrumbs": [
            {
                "title": _(u"Validation overview"),
                "url": "/session/{}".format(code)
            },
            {
                "title": title,
                "url": None
            }
        ]
    })

    return params


@view_config(route_name='css_error_details',
             renderer='templates/css_error_details.pt')
def css_error_details(request):
    code = request.matchdict['code']
    errorhash = request.matchdict['errorhash']

    CSSModel = get_css_validator_model(code)
    query = DBSession.query(CSSModel).filter(CSSModel.errorhash == errorhash)

    if query.count() == 0:
        # TODO: complete
        raise Exception

    results = {}
    error_message = None
    for row in query:
        if not error_message:
            error_message = row.error
        urlhash = row.urlhash
        if urlhash not in results:
            results[urlhash] = {
                "total": 0,
                "urlhash": urlhash,
                "url": row.url,
                'errortype': row.errortype,
                'references': []
            }
        error = results[urlhash]
        error['total'] += 1
        error["references"].append({
            'position': "L {}".format(row.line),
            'url': row.url,
            'context': row.context,
            'source': row.source
        })

    title = _(u'CSS Error details')
    params = base_view_params(request, title).copy()
    params.update({
        "urls": results,
        "error_message": error_message,
        "code": code,
        "breadcrumbs": [
            {
                "title": _(u"Validation overview"),
                "url": "/session/{}".format(code)
            },
            {
                "title": title,
                "url": None
            }
        ]
    })

    return params
