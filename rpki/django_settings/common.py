# $Id$

# Copyright (C) 2015-2016  Parsons Government Services ("PARSONS")
# Portions copyright (C) 2014  Dragon Research Labs ("DRL")
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notices and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND PARSONS AND DRL DISCLAIM ALL
# WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN NO EVENT SHALL
# PARSONS OR DRL BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION
# WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

"""
This module contains common configuration settings for Django libraries.

Most of our CA code uses at least the Django ORM; the web interface
uses a lot more of Django.  We also want to handle all normal user
configuration via rpki.conf, so some of the code here is just pulling
settings from rpki.conf and stuffing them into the form Django wants.
"""

__version__ = "$Id$"

import os
import rpki.config
import rpki.autoconf

# Some configuration, including SQL authorization, comes from rpki.conf.
cfg = rpki.config.parser()


# Do -not- turn on DEBUG here except for short-lived tests, otherwise
# long-running programs like irdbd will eventually run out of memory
# and crash.  This is also why this is controlled by an environment
# variable rather than by an rpki.conf setting: just because we want
# debugging enabled in the GUI doesn't mean we want it in irdb.
#
# If you must enable debugging, you may need to add code that uses
# django.db.reset_queries() to clear the query list manually, but it's
# probably better just to run with debugging disabled, since that's
# the expectation for production code.
#
# https://docs.djangoproject.com/en/dev/faq/models/#why-is-django-leaking-memory

if os.getenv("RPKI_DJANGO_DEBUG") == "yes":
    DEBUG = True


# Database configuration differs from program to program, but includes
# a lot of boilerplate.  So we define a class here to handle this,
# then use it and clean up in the modules that import from this one.

class DatabaseConfigurator(object):

    default_sql_engine = "mysql"
    cfg     = None
    section = None

    def configure(self, cfg, section):  # pylint: disable=W0621
        self.cfg = cfg
        self.section = section
        engine = cfg.get("sql-engine", section = section,
                         default = self.default_sql_engine)
        return dict(
            default = getattr(self, engine))

    @property
    def mysql(self):
        return dict(
            ENGINE   = "django.db.backends.mysql",
            NAME     = cfg.get("sql-database", section = self.section),
            USER     = cfg.get("sql-username", section = self.section),
            PASSWORD = cfg.get("sql-password", section = self.section),
            #
            # Using "latin1" here is totally evil and wrong, but
            # without it MySQL 5.6 (and, probably, later versions)
            # whine incessantly about bad UTF-8 characters in BLOB
            # columns.  Which makes no freaking sense at all, but this
            # is MySQL, which has the character set management interface
            # from hell, so good luck with that.  If anybody really
            # understands how to fix this, tell me; for now, we force
            # MySQL to revert to the default behavior in MySQL 5.5.
            #
            OPTIONS  = dict(charset = "latin1"))

    @property
    def sqlite3(self):
        return dict(
            ENGINE   = "django.db.backends.sqlite3",
            NAME     = cfg.get("sql-database", section = self.section))

    @property
    def postgresql(self):
        return dict(
            ENGINE   = "django.db.backends.postgresql_psycopg2",
            NAME     = cfg.get("sql-database", section = self.section),
            USER     = cfg.get("sql-username", section = self.section),
            PASSWORD = cfg.get("sql-password", section = self.section))


# Apps are also handled by the modules that import this one, now that
# we don't require South.


# Silence whining about MIDDLEWARE_CLASSES

MIDDLEWARE_CLASSES = ()

# That would be it if we just need the ORM, but Django throws a hissy
# fit if SECRET_KEY isn't set, whether we use it for anything or not.
#
# Make this unique, and don't share it with anybody.
if cfg.has_option("secret-key", section = "web_portal"):
    SECRET_KEY = cfg.get("secret-key", section = "web_portal")
else:
    SECRET_KEY = os.urandom(66).encode("hex")


# Django defaults to thinking everybody lives in Chicago.

TIME_ZONE = "UTC"
