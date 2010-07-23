# Django settings for snippy project.
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = PROJECT_ROOT + '/db.sqlite'

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = PROJECT_ROOT + '/media/'

TEX_MEDIA = MEDIA_ROOT + '/TeX/'

UPLOAD_PATH = MEDIA_ROOT + '/uploads/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
TEX_MEDIA_URL = MEDIA_URL + '/TeX/'
UPLOAD_URL = MEDIA_URL + '/uploads/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'django_stats.middleware.StatsMiddleware',
    # he pingback specs also allow publishing the pingback url
    # via an HTTP X-Header. To enable this feature decomment
    # the following line
    #'trackback.middleware.PingbackUrlInjectionMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'yadb.context_processors.version',
    'django.core.context_processors.request',
)


TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates/',
)


PINGBACK_RESOLVERS = (
    'trackback.utils.resolvers.decorated',
    'trackback.utils.resolvers.generic_view',
)

STATS_BLACKLIST = {
    'path': (r'^/media/', r'^/admin/'),
    'user agent': (r'Googlebot', r'YandexBot', r'Baiduspider'),
}

INSTALLED_APPS = (
    # to make 'auth' tests work
    # you have to include 'django.contrib.admin'
    # http://osdir.com/ml/DjangoUsers/2009-05/msg00972.html
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.flatpages',
    'django.contrib.comments',
    'pagination',
    'trackback',
    'tagging',
    'yadb',
    'django_stats',
)

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'

DEBUG = False

SNIPPY_GIT_VERSION = '-zer0'

PREVIEW_POST_LENGTH = 150

try:
    from version import SNIPPY_GIT_VERSION
except ImportError:
    print '*** No \'version.py\' or doesn\'t contain SNIPPY_GIT_VERSION'

try:
    from local_settings import *
except ImportError:
    print '*** Do you have a \'local_settings.py\'?'

MANAGERS = ADMINS
TEMPLATE_DEBUG = DEBUG
