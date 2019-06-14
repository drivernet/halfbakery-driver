__site_url__ = 'http://www.halfbakery.com'
__base_url__ = 'https://www.halfbakery.com/lr/'

from tqdm import tqdm
from metadrive._requests import get_drive


def _login(
        username=None,
        password=None,
        drive=None,
        refresh=False,
        recreate_profile=False,
        profile='halfbakery:default',
        proxies='default',
    ):

    if drive is None:

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
