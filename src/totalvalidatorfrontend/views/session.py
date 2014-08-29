# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

from sqlalchemy import func

from ..config import DATETIME_FORMAT
from ..config import SESSION_STATUS
from ..models import DBSession
from ..models import create_or_clean_tables
from ..models import get_accessibility_validator_model
from ..models import get_css_validator_model
from ..models import get_markup_validator_model
from ..models import get_urls_model
from ..task import CrawlingTask

from ..utils import get_validation_session
from .utils import base_view_params

from .. import messageFactory as _


@view_config(route_name='overview',
             renderer='templates/overview.pt',
             permission='view')
def overview(request):
    code = request.matchdict['code']
    session = get_validation_session(code)

    params = base_view_params(request, session.url).copy()

    URLModel = get_urls_model(code)

    # Errors per url

    url_query = DBSession.query(URLModel)
    n_urls = url_query.count()
    urls = []
    total_markup_errors = {
        'warning': 0,
        'error': 0
    }

    total_accessibility_errors = {
        'warning': 0,
        'error': 0
    }

    for url in url_query:
        date = _(u"Validating")
        if url.date:
            date = url.date.strftime(DATETIME_FORMAT)

        item = {
            "id": url.id,
            "url": url.url,
            "date": date,
            "markup_errors": [],
            "accessibility_errors": []
        }
        if session.status == 3:
            error_markup = url.error_markup
            warning_markup = url.warning_markup

            total_markup_errors['error'] += error_markup
            total_markup_errors['warning'] += warning_markup

            if (warning_markup + error_markup) == 0:
                item['markup_errors'] = [
                    {
                        "class": "label label-success",
                        "title": _(u"No errors found"),
                        "errors": "OK"
                    }
                ]
            else:
                item['markup_errors'] = [
                    {
                        "class": "label label-warning",
                        "title": _(u"N. of warnings"),
                        "errors": warning_markup
                    },
                    {
                        "class": "label label-error",
                        "title": _(u"N. of errors"),
                        "errors": error_markup
                    }
                ]

            error_accessibility = url.error_accessibility
            warning_accessibility = url.warning_accessibility

            total_accessibility_errors['error'] += error_accessibility
            total_accessibility_errors['warning'] += warning_accessibility

            if (error_accessibility + warning_accessibility) == 0:
                item['accessibility_errors'] = [
                    {
                        "class": "label label-success",
                        "title": _(u"No errors found"),
                        "errors": "OK"
                    }
                ]
            else:
                item['accessibility_errors'] = [
                    {
                        "class": "label label-warning",
                        "title": _(u"N. of warnings"),
                        "errors": warning_accessibility
                    },
                    {
                        "class": "label label-error",
                        "title": _(u"N. of errors"),
                        "errors": error_accessibility
                    }
                ]

        urls.append(item)

    # markup errors
    MarkupModel = get_markup_validator_model(code)
    markup_query = DBSession.query(
        func.count(MarkupModel.errorhash).label("total"),
        MarkupModel.error,
        MarkupModel.type,
        MarkupModel.errorhash
    ).group_by(MarkupModel.errorhash).order_by(MarkupModel.type)

    # Accessibility errors
    AccessiblityModel = get_accessibility_validator_model(code)
    accessibility_query = DBSession.query(
        func.count(AccessiblityModel.errorhash).label("total"),
        AccessiblityModel.error,
        AccessiblityModel.type,
        AccessiblityModel.errorhash
    ).group_by(AccessiblityModel.errorhash).order_by(AccessiblityModel.type)

    # CSS Errors
    css_errors = {}
    total_css_errors = {
        'warning': 0,
        'error': 0
    }
    if session.status == 3:
        CSSModel = get_css_validator_model(code)
        css_query = DBSession.query(CSSModel)

        for row in css_query:
            hash_ = row.urlhash
            if hash_ not in css_errors:
                css_errors[hash_] = {
                    'url': row.url,
                    'warning': 0,
                    'error': 0,
                }
            item = css_errors[hash_]
            error_type = item.get(row.type)
            if error_type is None:
                continue
            item[row.type] += 1
            total_css_errors[row.type] += 1

    extra_params = {
        "css_errors": css_errors,
        "total_css_errors": total_css_errors,
        "session_code": code,
        "markup_errors": markup_query,
        "total_markup_errors": total_markup_errors,
        "accessibility_errors": accessibility_query,
        "total_accessibility_errors": total_accessibility_errors,
        "n_urls": n_urls,
        "urls": urls,
        "status": SESSION_STATUS.get(session.status),
        "status_code": session.status,
        "breadcrumbs": [
            {"title": _(u"Validation overview"), "url": None}
        ]
    }
    params.update(extra_params)

    return params


@view_config(route_name="validate", permission='validate')
def validate(request):
    code = request.matchdict['code']
    session = get_validation_session(code)

    # 1. clean all tables
    create_or_clean_tables(code)

    # 2. change session status
    session.status = 1
    DBSession.flush()

    # 3. revalidate
    crawling = CrawlingTask()
    crawling.delay(session)

    url = request.route_url('overview', code=code)
    return HTTPFound(location=url)


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
