__site_url__ = 'http://www.halfbakery.com'
__base_url__ = 'http://www.halfbakery.com'

import os
import requests

from metadrive import utils

from halfbakery.api import (
    Topic,
    Comment
)


def _login(username=None, password=None):
    '''
    Creates, serializes and saves session
    ( utils.save_session_data )
    '''

    session = requests.Session()
    session.metaname = utils.get_metaname('halfbakery')
    session_data = utils.load_session_data(namespace='halfbakery')

    if session_data:
        session.cookies.update(
            requests.utils.cookiejar_from_dict(
                session_data))
        return session

    if not username and password:
        credential = utils.get_or_ask_credentials(
            namespace='halfbakery',
            variables=['username', 'password'])

        username = credential['username']
        password = credential['password']

    if session.get('http://www.halfbakery.com/lr/').ok:
        signin = session.get('http://www.halfbakery.com/lr/',
             params={
                 'username': username,
                 'password': password,
                 'login': 'login'})

        if signin.ok:
            utils.save_session_data(
                'halfbakery',
                requests.utils.dict_from_cookiejar(
                    session.cookies))

            return session
        else:
            raise Exception(
                'Could not signin: {}'.format(
                    signin.status_code))
    else:
        raise Exception(
            'Failed to open Halfbakery: {}'.format(
                signin.status_code))


def _harvest(query=None, limit=None, get_detail=False):
    '''
    Combines login, get, search into a procudure
    sufficient to generate full-fledged items.
    '''

    session = _login()

    for item in Topic._filter(
            query=query,
            session=session,
            get_detail=get_detail,
            limit=limit):

        yield item
