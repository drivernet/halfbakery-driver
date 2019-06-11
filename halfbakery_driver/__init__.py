__site_url__ = 'http://www.halfbakery.com'
__base_url__ = 'https://www.halfbakery.com/lr/'

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



def _harvest():
    from tqdm import tqdm
    import metadrive #noqa
    from halfbakery_driver.api import Category #noqa

    drive = metadrive.drives.get('halfbakery_driver:default')

    for category in tqdm(Category._filter(drive=drive)):
        category.save()

    # (will also save comments, users, cause they are part of ideas)
    # for idea in tqdm(Idea._filter(drive=drive)):
    #     idea.save()

    # :UNNECESSARY:
    #
    # for user in tqdm(User._filter(drive=drive)):
    #     user.save()

    # for comment in tqdm(Comment._filter(drive=drive)):
    #     comment.save()
