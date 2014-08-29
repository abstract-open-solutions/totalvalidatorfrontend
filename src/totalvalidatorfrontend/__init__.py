# -*- encoding: utf-8 -*-
import deform

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import RepozeWho1AuthenticationPolicy

from pyramid_who.whov2 import WhoV2AuthenticationPolicy


from pyramid.config import Configurator
from pyramid.i18n import TranslationStringFactory
from pyramid.session import UnencryptedCookieSessionFactoryConfig
from pyramid.i18n import default_locale_negotiator
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

    config = Configurator(
        settings=settings,
        session_factory=_session_factory,
        root_factory='.models.RootFactory'
    )

    # config_file = '/Users/giorgio/sviluppo/abstract/totalvalidator_frontend/etc/who.ini'
    # authentication_policy = WhoV2AuthenticationPolicy(
    #     config_file,
    #     "auth_tkt_plugin",
    #     # callback=verify_user
    # )

    authentication_policy = RepozeWho1AuthenticationPolicy(
        identifier_name="__ac",
    )
    config.set_authentication_policy(authentication_policy)

    authorization_policy = ACLAuthorizationPolicy()
    config.set_authorization_policy(authorization_policy)

    config.include('pyramid_chameleon')

    from .forms import get_deform_renderer
    deform.Form.set_default_renderer(
        config.maybe_dotted(get_deform_renderer())
    )

    config.add_static_view(
        'static',
        'static',
        permission='public',
        cache_max_age=3600
    )

    # internationalization
    config.add_translation_dirs(
        'totalvalidatorfrontend:locale/',
        'colander:locale',
        'deform:locale',
    )
    config.set_locale_negotiator(default_locale_negotiator)

    # routes
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
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
