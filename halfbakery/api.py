import bs4

from metatype import Dict
from halfbakery import __base_url__

class User(Dict):
    @classmethod
    def _filter(cls, drive, keyword=None):
        raise NotImplemented

    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _create(cls):
        raise NotImplemented


class Category(Dict):

    @classmethod
    def _filter(cls, drive, keyword=None, from_disk=False):

        drive.get('https://www.halfbakery.com/lr/view/s=c:d=c:dh=1:dn=100:ds=A:n=categories:i=:t=All_20Categories')
        soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')

        for item in soup.find_all('item'):
            yield cls({
                'cateogry': item.title.text,
                '-': item.attrs.get('rdf:about'),
                '@': drive.spec + cls.__name__
            })

    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _create(cls):
        raise NotImplemented


class Idea(Dict):

    def _refresh(self):
        if self.get('-') is not None:
            url = self.get('-')

            if 'www.halfbakery.com' in url and  'www.halfbakery.com/lr' not in url:
                url = url.replace('www.halfbakery.com', 'www.halfbakery.com/lr')

            self.drive.get(url)
            soup = bs4.BeautifulSoup(self.drive.response.content, 'html.parser')

            record = dict()

            # record['title'] =
            # record['subtitle'] =
            # record['description'] =
            # record['fishbones'] =
            # record['croissants'] =
            # record['annotations'] =  [Comment(), Comment()...]

            self.update(record)


    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _filter(cls,
                drive,
                keyword=None,
                search='',
                filter_type='Q',
                window_size=100,
                window_position=0,
                return_format=1,
                return_properties='iocwvrqh',
                strategy='by_category',
                ):

        '''
        A method to be used for periodically synchronized. Howver, how it is different from harvest?
        # probably the best way to keep up with the new data, is to track view filtered by "last_modified",

        :strategy: by_category - go through every category
        '''
        filter_types = {
         'Q': 'modification date',
         'R': 'creation date',
         'r': 'creation date (earliest first)',
         'F': 'number of search matches',
         'c': 'category',
         'd': 'major category',
         'o': 'author',
         'i': 'idea name',
         'U': 'votes',
         'u': 'votes (worst first)',
         'X': 'conflicting votes',
         'E': 'your last change',
        }

        return_formats = {
         '1': 'table',
         'A': 'RSS 1.0',
         '0': 'unstructured list of names',
         '3': 'group in three columns',
         '9': 'RSS 0.91',
        }

        return_properties = {
         'i': 'idea title',
         'h': 'idea subtitle',
         'o': 'author',
         'c': 'category',
         'w': 'votes meal sign',
         'v': 'votes',
         'r': 'creation date',
         'q': 'modification date (last anno date)',
         'e': '??? some kind of date',
         'j': '??? note/link',
         'u': '??? also votes/meal sign',
         'x': '??? some kind of numbers',
         'y': '??? some kind of numbers',
        }

        if search:
            # (search) variant A:
            search_url = '{base}?searchexpression={keyword}&ok=OK'.format(
                base=__base_url__,
                keyword=search or ''
            )
            print(search_url)
            # drive.get(search_url)
        else:
            # (view) variant B:
            filter_url = '{base}view/s={s}:d={d}:dh={dh}:dn={dn}:do={do}:ds={ds}:n={n}:i=:t='.format(
                base=__base_url__,
                s  = filter_type or '',
                dn = window_size or '',     # 1..N
                do = window_position or '', # 0..M
                ds = return_format or '',
                d  = return_properties or '',
                n  = view_title or '',       # any name
            )
            print(filter_url)
            # drive.get(filter_url)


    @classmethod
    def _create(cls):
        raise NotImplemented

    def annotations(self):
        raise NotImplemented

    def update_vote(self, value):
        raise NotImplemented


class Annotation(Dict):

    @classmethod
    def _filter(cls):
        raise NotImplemented

    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _create(cls):
        raise NotImplemented
