# -*- encoding: utf-8 -*-
from pyramid.renderers import get_renderer
from sqlalchemy import func
from ..models import DBSession
from ..models import get_markup_validator_model
from ..models import get_urls_model
from ..utils import get_validation_session
from ..models import get_css_validator_model


def get_n_pages(session_code):
    session = get_validation_session(session_code)
    pages = ''
    if session.status == 3:
        Model = get_urls_model(session_code)
        pages = DBSession.query(Model.id).count()
    return pages


def get_errors(session_code):
    Model = get_urls_model(session_code)
    query = DBSession.query(
        func.sum(Model.warning_markup).label("warning_markup"),
        func.sum(Model.error_markup).label("error_markup"),
        func.sum(Model.info_accessibility).label("info_accessibility"),
        func.sum(Model.warning_accessibility).label("warning_accessibility"),
        func.sum(Model.error_accessibility).label("error_accessibility"),
    )

    errors = {
        'markup': [
            {
                "attr": "warning_markup",
                "class": "label label-warning",
                "title": "N. of warnings",
                "errors": 0
            },
            {
                "attr": "error_markup",
                "class": "label label-error",
                "title": "N. of errors",
                "errors": 0
            }
        ],
        'accessibility': [
            {
                "attr": "warning_accessibility",
                "class": "label label-warning",
                "title": "N. of warnings",
                "number": 0
            },
            {
                "attr": "error_accessibility",
                "class": "label label-error",
                "title": "N. of errors",
                "number": 0
            }
        ]
    }

    if query.count() == 1:
        results = query.one()

        for k, group in errors.items():
            has_error = False
            for item in group:
                if not item['attr']:
                    continue
                num = getattr(results, item['attr'])
                if num > 0:
                    has_error = True
                item['errors'] = num
            if not has_error:
                errors[k] = [
                    {
                        "attr": None,
                        "class": "label label-success",
                        "title": "No errors found",
                        "errors": "OK"
                    }
                ]
    CSSModel = get_css_validator_model(session_code)
    query_css = DBSession.query(CSSModel)
    css_errors = {
        'warning': 0,
        'error': 0
    }

    for row in query_css:
        if css_errors.get(row.type) is None:
            continue
        css_errors[row.type] += 1

    errors['css'] = [
        {
            "class": "label label-warning",
            "title": "N. of warnings",
            "errors": css_errors["warning"]
        },
        {
            "class": "label label-error",
            "title": "N. of errors",
            "errors": css_errors["error"]
        }
    ]

    return errors


def set_status_message(request, message, type_='info'):
    _message = {
        "message": message,
        "class": 'alert-{}'.format(type_)
    }
    request.session.flash(_message)


def base_view_params(request, title, active_menu=None):
    renderer = get_renderer('templates/main.pt')
    # set_active = lambda x, y: (x is not None and x == y) and 'active' or None
    params = {
        'status_messages': request.session.pop_flash(),
        'username': None,
        'main': renderer.implementation(),
        'title': title,
        'actions': [
            # {
            #     'url': "./new",
            #     'title': 'Create new validation session',
            #     'content': 'New session',
            #     'class': set_active(active_menu, 'new_session'),
            #     'id': 'new_session'
            # },
            # {
            #     'url': "http://www.abstract.it",
            #     'title': 'vai al sito di Abstract',
            #     'content': 'Abstract',
            #     'class': set_active(active_menu, 'abstract_site'),
            #     'id': 'abstract_site'
            # },
        ],
    }
    return params


def errors_formatter(query):
    results = {}
    errors_total = 0
    for item in query:
        if item.error not in results:
            results[item.error] = {
                "total": 0,
                "references": []
            }
        error = results[item.error]
        error["total"] += 1
        errors_total += 1
        error["detail"] = item.detail
        if item.source or item.line or item.column:
            error["references"].append({
                "position": "L {} C {}".format(item.line, item.column),
                "source": item.source,
            })
    return errors_total, results
