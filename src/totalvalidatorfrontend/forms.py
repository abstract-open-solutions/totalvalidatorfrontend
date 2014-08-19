import colander
from deform import Form
from deform.schema import FileData
from deform.widget import CheckboxChoiceWidget
from pyramid.view import view_config


VALIDATORS = (
    ('html', 'HTML Markup'),
    ('accessibility', 'Accessibility'),
    ('css', 'CSS')
)


class Session(colander.MappingSchema):
    """Validation session's form schema"""
    url = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(max=255)
    )

    limit = colander.SchemaNode(
        colander.Integer(),
        default=5
    )

    checker = colander.SchemaNode(
        colander.Set(),
        widget=CheckboxChoiceWidget(values=VALIDATORS),
        validator=colander.Length(min=1),
        default=('html',)
    )


def new_session_form():
    """Return a Deform form for validation session."""
    schema = Session()
    _form = Form(schema, buttons=('Validate',))
    return _form
