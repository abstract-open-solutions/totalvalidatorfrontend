# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from sqlalchemy import func

from ..config import DATETIME_FORMAT
from ..models import DBSession
from ..models import get_accessibility_validator_model
from ..models import get_markup_validator_model
from ..models import get_urls_model

from .utils import base_view_params
from .utils import markup_errors_formatter
from .utils import accessiblity_errors_formatter

from .. import messageFactory as _


@view_config(route_name='url_details',
             renderer='templates/url_details.pt',
             permission='view')
def url_details(request):
    code = request.matchdict['code']
    url_id = request.matchdict['id']

    URLModel = get_urls_model(code)
    MarkupModel = get_markup_validator_model(code)
    AccessibilityModel = get_accessibility_validator_model(code)

    url = DBSession.query(URLModel).filter(URLModel.id == url_id).one()
    title = _(u"Page validation details")

    params = base_view_params(request, title).copy()

    markup_query = DBSession.query(MarkupModel).join(
        URLModel, MarkupModel.url == URLModel.url
    ).filter(
        URLModel.id == url_id
    ).order_by(MarkupModel.type)

    markup_errors = markup_errors_formatter(
        markup_query.filter(MarkupModel.type == 'error')
    )

    markup_warnings = markup_errors_formatter(
        markup_query.filter(MarkupModel.type == 'warning'),
    )

    accessibility_query = DBSession.query(AccessibilityModel).join(
        URLModel, AccessibilityModel.url == URLModel.url
    ).filter(
        URLModel.id == url_id
    ).order_by(AccessibilityModel.type)

    accessibility_errors = accessiblity_errors_formatter(
        accessibility_query.filter(AccessibilityModel.type == 'error'),
    )
    accessibility_warnings = accessiblity_errors_formatter(
        accessibility_query.filter(AccessibilityModel.type == 'warning'),
    )

    params.update({
        "markup_errors": markup_errors[1],
        "n_markup_errors": markup_errors[0],
        "markup_warnings": markup_warnings[1],
        "n_markup_warnings": markup_warnings[0],
        "accessibility_errors": accessibility_errors[1],
        "n_accessibility_errors": accessibility_errors[0],
        "accessibility_warnings": accessibility_warnings[1],
        "n_accessibility_warnings": accessibility_warnings[0],
        "url": url.url,
        "last_check": url.date.strftime(DATETIME_FORMAT),
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
