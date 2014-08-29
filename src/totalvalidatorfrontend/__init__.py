from pyramid.config import Configurator
from pyramid.i18n import default_locale_negotiator
from pyramid.i18n import TranslationStringFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from sqlalchemy import engine_from_config

from .models import DBSession
from .models import Base

messageFactory = TranslationStringFactory('totalvalidatorfrontend')


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    # Base.metadata.create_all(engine)
    # create only session table
    # other tables will be created on demand
    Base.metadata.tables['session'].create(checkfirst=True)
    _session_factory = UnencryptedCookieSessionFactoryConfig('totalvalidator')

    config = Configurator(settings=settings, session_factory=_session_factory)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    # internationalization
    config.add_translation_dirs('totalvalidatorfrontend:locale/')
    config.set_locale_negotiator(default_locale_negotiator)

    # routes
    config.add_route('home', '/')
    config.add_route('set_lang', '/set_lang')
    config.add_route('new_session', '/new')
    config.add_route('delete', '/delete/{code}')
    config.add_route('overview', '/session/{code}')
    config.add_route('validate', '/session/{code}/validate')
    config.add_route('url_details', '/session/{code}/url/{id}')
    config.add_route('css_url_details', '/session/{code}/css_url/{urlhash}')
    config.add_route(
        'css_error_details', '/session/{code}/css_error/{errorhash}'
    )
    config.add_route(
        'markup_error_details',
        '/session/{code}/markup_error/{errorhash}'
    )
    config.add_route(
        'accessiblity_error_details',
        '/session/{code}/accessibility_error/{errorhash}'
    )

    config.scan()

    return config.make_wsgi_app()
