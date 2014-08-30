# -*- encoding: utf-8 -*-
import csv
import hashlib
import os
import subprocess
import transaction

from celery import Task
from celery.task.sets import subtask
from datetime import datetime
from pyramid.threadlocal import get_current_registry

from .models import get_urls_model
from .models import get_accessibility_validator_model
from .models import create_or_clean_tables

from .models import ValidationSessionModel
from .models import DBSession
from .utils import dict_to_unicode
from .utils import import_markup_data
from .utils import import_css_data
from .utils import import_accessibility_data
from .utils import update_errors_totals


class CrawlingTask(Task):

    def on_success(self, retval, task_id, *args, **kwargs):
        """When the urls are retrieved they will imported
        in 'urls' table and it will execute the check with a specific task.
        """
        session_id = args[0][0].id
        out_directory = retval[1]
        hash_ = retval[0]

        # 1. get the session
        session = DBSession.query(ValidationSessionModel).filter(
            ValidationSessionModel.id == session_id
        ).one()
        # 2. change session status
        session.status = 2

        # 2.a create all tables or clean them
        create_or_clean_tables(session.code)

        # 3. Rebuild urls table
        urls_model = get_urls_model(session.code)
        fp = open('/'.join((out_directory, 'pages.csv')))
        for url in fp:
            record = urls_model(url=url.strip())
            DBSession.add(record)
        fp.close()
        transaction.commit()

        # 4. run validation subtask
        checking = CheckTask()
        subtask(checking).delay(hash_, session_id)

    def run(self, record, user=None, password=None):
        """Call totalvalidator crawl command to get
        the urls to validate.

        When finished it calls "CheckTask" sub task.
        """
        registry = get_current_registry()
        path = registry.settings['totalvalidator.basepath']
        bin = registry.settings['totalvalidator.bin']

        sha = hashlib.sha1(record.url)
        hash_ = sha.hexdigest()

        directory = '{}/{}/crawl'.format(path, hash_)

        if not os.path.exists(directory):
            os.makedirs(directory)

        command = "{} crawl " .format(bin)
        if record.limit > 0:
            command += " -L {} ".format(record.limit)

        # TODO: user and password options

        command += '{} {}'.format(record.url, directory)
        proc = subprocess.Popen([command], shell=True)
        proc.wait()
        return hash_, directory


class CheckTask(Task):

    def on_success(self, retval, task_id, *args, **kwargs):
        """Populate DB tables with the output of totalvalidator"""
        hash_ = retval[0]
        out_directory = retval[1]
        if out_directory.endswith('/'):
            out_directory = out_directory[:-1]

        session_id = args[0][1]
        session = DBSession.query(ValidationSessionModel).filter(
            ValidationSessionModel.id == session_id
        ).one()

        # 1. Import data from CSV Files

        # 1.1. Markup validation data
        file_path = '/'.join((out_directory, 'markup.csv'))
        import_markup_data(file_path, session.code)
        # Flush the session to make data available
        DBSession.flush()

        # 1.2. CSS validation data
        file_path = '/'.join((out_directory, 'css.csv'))
        import_css_data(file_path, session.code)
        # Flush the session to make data available
        DBSession.flush()

        # 1.3. Accessibility validation data
        file_path = '/'.join((out_directory, 'accessibility.csv'))
        import_accessibility_data(file_path, session.code)
        # Flush the session to make data available
        DBSession.flush()

        # 2. Update errors totals in urls table
        update_errors_totals(session)
        # Flush the session to make data available
        DBSession.flush()

        # 3. Update session's status and date
        now = datetime.now()
        session.status = 3
        session.date = now

        # 4. update single url validation date
        urls_model = get_urls_model(session.code)
        DBSession.query(urls_model).update({"date": now})

        transaction.commit()

    def run(self, hash_, session_id):
        """Call totalvalidator check command to validate
        the urls crawled before by CrawlingTask.

        When finished it populates related tables.
        """
        registry = get_current_registry()
        path = registry.settings['totalvalidator.basepath']
        bin = registry.settings['totalvalidator.bin']
        conf_file = registry.settings['totalvalidator.conf']

        src_directory = '{}/{}/crawl'.format(path, hash_)
        des_directory = '{}/{}/check'.format(path, hash_)

        if not os.path.exists(des_directory):
            os.makedirs(des_directory)

        command = "{} check {} {} {}".format(
            bin,
            conf_file,
            src_directory,
            des_directory
        )

        proc = subprocess.Popen([command], shell=True)
        proc.wait()
        return hash_, des_directory
