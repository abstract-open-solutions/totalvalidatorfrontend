# -*- encoding: utf-8 -*-
from pyramid.view import view_config
from sqlalchemy import func

from ..config import DATETIME_FORMAT
from ..config import SESSION_STATUS
from ..models import DBSession
from ..models import get_markup_validator_model
from ..models import get_urls_model
from ..utils import get_validation_session
from ..models import get_css_validator_model

from .utils import base_view_params
from .utils import errors_formatter


@view_config(route_name='overview', renderer='templates/overview.pt')
def overview(request):
    code = request.matchdict['code']
    session = get_validation_session(code)

    params = base_view_params(request, session.url).copy()

    URLModel = get_urls_model(code)

    MarkupModel = get_markup_validator_model(code)
    url_query = DBSession.query(URLModel)
    n_urls = url_query.count()
    urls = []
    total_markup_errors = {
        'warning': 0,
        'error': 0
    }

    for url in url_query:
        item = {
            "id": url.id,
            "url": url.url,
            "date": url.date.strftime(DATETIME_FORMAT),
            "markup_errors": []
        }
        if session.status == 3:
            warning_markup = url.warning_markup
            error_markup = url.error_markup

            total_markup_errors['error'] += error_markup
            total_markup_errors['warning'] += warning_markup

            if (warning_markup + error_markup) == 0:
                item['markup_errors'] = [
                    {
                        "class": "label label-success",
                        "title": "No errors found",
                        "errors": "OK"
                    }
                ]
            else:
                item['markup_errors'] = [
                    {
                        "class": "label label-warning",
                        "title": "N. of warnings",
                        "errors": warning_markup
                    },
                    {
                        "class": "label label-error",
                        "title": "N. of errors",
                        "errors": error_markup
                    }
                ]
        urls.append(item)

    markup_query = DBSession.query(
        func.count(MarkupModel.errorhash).label("total"),
        MarkupModel.error,
        MarkupModel.type,
        MarkupModel.errorhash
    ).group_by(MarkupModel.errorhash).order_by(MarkupModel.type)

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
        "n_urls": n_urls,
        "urls": urls,
        "status": SESSION_STATUS.get(session.status)
    }
    params.update(extra_params)

    return params


@view_config(route_name='url_details', renderer='templates/url_details.pt')
def url_details(request):
    code = request.matchdict['code']
    url_id = request.matchdict['id']

    URLModel = get_urls_model(code)
    MarkupModel = get_markup_validator_model(code)

    url = DBSession.query(URLModel).filter(URLModel.id == url_id).one()

    params = base_view_params(request, "Validation details").copy()

    markup_query = DBSession.query(MarkupModel).join(
        URLModel, MarkupModel.url == URLModel.url
    ).filter(
        URLModel.id == url_id
    ).order_by(MarkupModel.type)

    markup_errors = errors_formatter(
        markup_query.filter(MarkupModel.type == 'error')
    )

    markup_warnings = errors_formatter(
        markup_query.filter(MarkupModel.type == 'warning'),
    )

    params.update({
        "markup_errors": markup_errors[1],
        "n_markup_errors": markup_errors[0],
        "markup_warnings": markup_warnings[1],
        "n_markup_warnings": markup_warnings[0],
        "url": url.url,
        "last_check": url.date.strftime(DATETIME_FORMAT)
    })
    return params


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
        print item.id
        error["references"].append({
            "position": "L {} C {}".format(item.line, item.column),
            "source": item.source,
        })

    params = base_view_params(request, "Error details").copy()
    params.update({
        "results": results,
        "error_message": error_message,
        "details": details,
        "session_code": code,
    })
    return params
