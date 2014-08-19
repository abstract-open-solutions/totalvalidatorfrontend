# -*- encoding: utf-8 -*-
import csv
import hashlib
from datetime import datetime
from pyramid.httpexceptions import exception_response
from sqlalchemy import func

from .models import DBSession
from .models import ValidationSessionModel
from .models import get_accessibility_validator_model
from .models import get_css_validator_model
from .models import get_markup_validator_model
from .models import get_urls_model


def get_validation_session(session_code):
    """Return validation session by its code.

    :param session_code: validation session uuid
    :type session_code: string
    """
    query = DBSession.query(ValidationSessionModel).filter(
        ValidationSessionModel.code == session_code
    )
    if query.count() != 1:
        raise exception_response(404)
    return query.first()


def dict_to_unicode(dict_):
    """Convert all value of a dictionary to unicode.

    :param dict_: dictionary to convert
    :type dict_: dict
    """
    converted = {}
    for k in dict_.keys():
        value = dict_[k]
        if not isinstance(value, unicode):
            value = value.decode('utf-8')
        converted[k] = value
    return converted


def import_markup_data(filepath, session_code):
    """It reads a file and import all data in markup validation table.

    :param filepath: the CSV filepath
    :type filepath: path
    :param session_code: validation session uuid
    :type session_code: string
    """
    fp = open(filepath, 'r')
    reader = csv.DictReader(fp)
    Model = get_markup_validator_model(session_code)

    # Empty table
    DBSession.query(Model).delete()

    for item in reader:
        # Convert to Unicode
        row = dict_to_unicode(item)

        # Create an hash for each error message
        sha = hashlib.sha1(item["error"])
        row["errorhash"] = sha.hexdigest()
        DBSession.add(Model(**row))
    fp.close()


def import_css_data(filepath, session_code):
    """It reads a file and import all data in CSS validation table.

    :param filepath: the CSV filepath
    :type filepath: path
    :param session_code: validation session uuid
    :type session_code: string
    """

    fp = open(filepath, 'r')
    reader = csv.DictReader(fp)
    Model = get_css_validator_model(session_code)

    # url,type,line,error,source,context
    # Empty table
    DBSession.query(Model).delete()

    now = datetime.now()

    for item in reader:
        # convert to Unicode
        row = dict_to_unicode(item)

        row["date"] = now
        # Create an hash for each error and url
        sha = hashlib.sha1(item["error"])
        row["errorhash"] = sha.hexdigest()
        sha = hashlib.sha1(item["url"])
        row['urlhash'] = sha.hexdigest()
        DBSession.add(Model(**row))
    fp.close()


def import_accessibility_data(filepath, session_code):
    """It reads a CSV file and import all data in Accessibility
    validation table.

    :param filepath: the CSV filepath
    :type filepath: path
    :param session_code: validation session uuid
    :type session_code: string
    """
    # TODO:
    # reader = csv.DictReader(filepath)
    # Model = get_accessibility_validator_model(session_code)

    # # Empty table
    # DBSession.query(Model).delete()

    # for item in reader:
    #     # convert to Unicode
    #     row = dict_to_unicode(item)
    #     DBSession.add(Model(**row))


def update_errors_totals(session):
    """Update error totals in urls model by examine validator models.

    :param session: Validation session record
    :type session: ...
    """
    session_code = session.code
    UrlsModel = get_urls_model(session_code)
    MarkupModel = get_markup_validator_model(session_code)

    # error type | urls column
    error_types = {
        u"warning": "warning_markup",
        u"error": "error_markup",
        # commonly validator cannot retrieve the specified url
        u"Validator error": "error_markup"
    }

    query = DBSession.query(
        func.count(MarkupModel.type).label("n_errors"),
        MarkupModel.type,
        MarkupModel.url
    ).group_by(
        MarkupModel.url, MarkupModel.type
    ).order_by(
        MarkupModel.url, MarkupModel.type
    )

    for item in query:
        column = error_types.get(item.type)
        if not column:
            continue

        DBSession.query(UrlsModel).filter(
            UrlsModel.url == item.url
        ).update(
            {column: item.n_errors}
        )
