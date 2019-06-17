__site_url__ = 'http://www.halfbakery.com'
__base_url__ = 'https://www.halfbakery.com/lr/'

import bs4
import getpass
from tqdm import tqdm
from metadrive._requests import get_drive


def _login(
        username=None,
        password=None,
        drive=None,
        refresh=False,
        recreate_profile=False,
        profile='halfbakery-driver:default',
        proxies='default',
        interactive=False,
    ):

    if interactive:
        if username is None:
            username = input('Halfbakery username: ') or None
        if password is None:
            password = getpass.getpass('Halfbakery password: ') or None

    if drive is None:

        if username is not None:
            profile = 'halfbakery-driver:{}'.format(username)

        drive = get_drive(
            profile=profile,
            recreate_profile=recreate_profile,
            proxies=proxies)

    drive.get(__base_url__)

    if drive.response.ok:

        drive.get(__base_url__,
             params={
                 'username': username,
                 'password': password,
                 'login': 'login'})

        if drive.response.ok:

            soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')
            if soup.find('a', text='logout') is None:

                if username is None:

                    drive.get(__site_url__)
                    soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')
                    edit = soup.find('a', text='edit')

                    if edit is not None:
                        username = bs4.BeautifulSoup(repr(edit.parent).split(repr(edit))[0], 'html.parser').text.strip()
                    else:
                        username = None

            print('State: logged in as {}.'.format(username or '<unknown>'))

            return drive
        else:
            raise Exception(
                'Could not signin: {}'.format(
                    drive.response.status_code))
    else:
        raise Exception(
            'Failed to open Halfbakery: {}'.format(
                drive.response.status_code))

    return drive


def _harvest(drive=None, period=60):
    import time

    from halfbakery_driver.api import (
        Idea,
        Category,
        User
    )

    if drive is None:
        import metadrive
        drive = metadrive.drives.get('halfbakery-driver:default')

    while True:
        Idea._sync(drive=drive)
        Category._sync(drive=drive)
        User._sync(drive=drive)
        time.sleep(period)
