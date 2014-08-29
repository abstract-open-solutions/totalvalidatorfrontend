# -*- encoding: utf-8 -*-
from pyramid.view import view_config

from ..models import DBSession
from ..models import get_markup_validator_model
from ..models import get_accessibility_validator_model
from ..models import get_urls_model

from .utils import base_view_params

from .. import messageFactory as _


@view_config(route_name='markup_error_details',
             renderer='templates/markup_error_details.pt')
def markup_error_details(request):
    code = request.matchdict['code']
    errorhash = request.matchdict['errorhash']

    URLModel = get_urls_model(code)
    MarkupModel = get_markup_validator_model(code)

    query = DBSession.query(
        MarkupModel,
        URLModel.id.label("url_id")
    ).join(
        URLModel,
        URLModel.url == MarkupModel.url
    ).filter(
        MarkupModel.errorhash == errorhash
    )

    error_message = None
    details = None
    results = {}
    for result in query:
        item = result[0]
        if not error_message:
            error_message = item.error
            details = item.detail
        if not results.get(item.url):
            results[item.url] = {
                "total": 0,
                "references": [],
                "type": item.type
            }
        error = results[item.url]
        error["total"] += 1
        error["url_id"] = result[1]

        error["references"].append({
            "position": "L {} C {}".format(item.line, item.column),
            "source": item.source,
        })

    title = _(u"Error details")
    params = base_view_params(request, title).copy()
    params.update({
        "results": results,
        "error_message": error_message,
        "details": details,
        "session_code": code,
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


@view_config(route_name='accessiblity_error_details',
             renderer='templates/accessiblity_error_details.pt')
def accessiblity_error_details(request):
    code = request.matchdict['code']
    errorhash = request.matchdict['errorhash']

    URLModel = get_urls_model(code)
    AccessiblityModel = get_accessibility_validator_model(code)

    query = DBSession.query(
        AccessiblityModel,
        URLModel.id.label("url_id")
    ).join(
        URLModel,
        URLModel.url == AccessiblityModel.url
    ).filter(
        AccessiblityModel.errorhash == errorhash
    )

    error_message = None
    details = None
    results = {}
    for result in query:
        item = result[0]
        if not error_message:
            error_message = item.error
            details = item.repair
        if not results.get(item.url):
            results[item.url] = {
                "total": 0,
                "references": [],
                "type": item.type
            }
        error = results[item.url]
        error["total"] += 1
        error["url_id"] = result[1]

        error["references"].append({
            "position": "L {} C {}".format(item.line, item.column),
            "source": item.source,
        })

    title = _(u"Error details")
    params = base_view_params(request, title).copy()
    params.update({
        "results": results,
        "error_message": error_message,
        "details": details,
        "session_code": code,
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
