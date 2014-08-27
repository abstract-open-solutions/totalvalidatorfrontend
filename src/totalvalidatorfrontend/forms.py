import colander
from deform import Form
from deform.schema import FileData
from deform.widget import CheckboxChoiceWidget
from pyramid.view import view_config
from . import messageFactory as _


VALIDATORS = (
    ('html', 'HTML Markup'),
    ('accessibility', 'Accessibility'),
    ('css', 'CSS')
)


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


def new_session_form():
    """Return a Deform form for validation session."""
    schema = Session()
    _form = Form(schema, buttons=(_(u'Validate'),))
    return _form
