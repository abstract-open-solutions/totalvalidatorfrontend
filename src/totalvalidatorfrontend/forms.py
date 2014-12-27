# -*- encoding: utf-8 -*-
import colander
from deform import Form
from deform import Button
from deform import ZPTRendererFactory
from deform.schema import FileData
from deform.widget import HiddenWidget
from deform.widget import PasswordWidget
from pkg_resources import resource_filename
from pyramid.i18n import get_localizer
from pyramid.i18n import get_locale_name
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
from . import messageFactory as _

# from deform.widget import CheckboxChoiceWidget
# VALIDATORS = (
#     ('html', 'HTML Markup'),
#     ('accessibility', 'Accessibility'),
#     ('css', 'CSS')
# )


def deform_translator(term):
    return get_localizer(get_current_request()).translate(term)


def get_deform_renderer():
    deform_template_dir = resource_filename('deform', 'templates/')

    return ZPTRendererFactory(
        [deform_template_dir], translator=deform_translator)


def wrap_schema(schema, request):
    locale_name = get_locale_name(request)

    class Schema(schema):
        _LOCALE_ = colander.SchemaNode(
            colander.String(),
            widget=HiddenWidget(),
            default=locale_name)

    return Schema


class Session(colander.MappingSchema):
    """Validation session's form schema"""
    url = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255),
        title=_(u"Site url to validate")
    )

    limit = colander.SchemaNode(
        colander.Integer(),
        default=5,
        validator=colander.Range(0, 999),
        missing=0,
        title=_(u"Max number of page to validate"),
        description=_(
            u"Insert a number from 0 to 999 to limit "
            u"the number of page to validate. "
            u"0 value or no value mean no limit."
        )
    )

    # not used
    # checker = colander.SchemaNode(
    #     colander.Set(),
    #     widget=CheckboxChoiceWidget(values=VALIDATORS),
    #     validator=colander.Length(min=1),
    #     default=('html',)
    # )


def new_session_form(request):
    """Return a Deform form for validation session."""
    schema = wrap_schema(Session, request)()
    _form = Form(schema, buttons=(_(u'Validate'),))
    return _form


class Login(colander.MappingSchema):
    """Validation session's form schema"""
    login = colander.SchemaNode(
        colander.String(),
        title=_(u"Username")
    )

    password = colander.SchemaNode(
        colander.String(),
        widget=PasswordWidget(),
        title=_(u"Password")
    )


def login_form(request):
    """Return a Deform form for login."""
    schema = wrap_schema(Login, request)()
    _form = Form(schema, buttons=(_(u'Login'),))
    return _form


class DeleteConfirmation(colander.MappingSchema):
    """Delete confirmation form schema"""
    confirm = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
        default=1
    )


def delete_confirmation_form(request):
    """Return a Deform form for delete confirmation."""
    schema = wrap_schema(DeleteConfirmation, request)()

    buttons = [
        Button(
            name='delete',
            title=_(u"Delete"),
            type='submit',
            css_class="btn btn-danger"
        ),
        Button(
            name='cancel',
            title=_(u"Cancel"),
            type='submit',
            css_class="btn btn-default"
        ),
    ]
    _form = Form(schema, buttons=buttons)
    return _form
