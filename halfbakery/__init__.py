__site_url__ = 'http://www.halfbakery.com'
__base_url__ = 'http://www.halfbakery.com/lr/'

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

    drive.get('http://www.halfbakery.com/lr/')

    if drive.response.ok:
        drive.get('http://www.halfbakery.com/lr/',
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


def _harvest():
    raise NotImplemented
