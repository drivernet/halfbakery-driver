import bs4

from metatype import Dict
from halfbakery import __base_url__

from dateutil.parser import parse as dateparse
from datetime import timezone

from halfbakery import utils


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

    def _refresh(self):

        if self.get('-') is not None:

            url = self['-']
            self.drive.get(url)
            soup = bs4.BeautifulSoup(self.drive.response.content, 'html.parser')

            record = dict()
            record['cateogry_title'] = soup.find('span', {'class': 'fhxl'}).text
            record['category_rss_url'] = 'https://www.halfbakery.com'+soup.find('a', text='rss').attrs['href']
            record['ideas_in_category'] = [
                {
                    'title': idea.text,
                    '-': 'https://www.halfbakery.com'+idea.attrs['href'].split('#', 1)[0],
                    'votes': idea.parent.parent.find('img') and utils.raw_votes_parse(idea.parent.parent.find('img').attrs.get('alt')) or None
                }
                for idea in soup.find_all('a', {'class': ['oldidea', 'newidea']})
            ]

            self.update(record)

    @classmethod
    def _filter(cls, drive, keyword=None, from_disk=False):

        drive.get('https://www.halfbakery.com/lr/view/s=c:d=c:dh=1:dn=100:ds=1:n=categories:i=:t=All_20Categories')

        soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')

        for item in soup.find_all('a', {'class': 'fcm'}):
            instance = cls({
                'cateogry': item.text,
                '-': 'https://www.halfbakery.com' + item.attrs.get('href'),
                '@': drive.spec + cls.__name__
            })
            instance.drive = drive
            yield instance

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
            #record['category'] =
            record['title'] = soup.find('a', {'name': 'idea'}).text
            record['subtitle'] = self.drive.response.text.split(']<br>', 1)[-1].split('<p>', 1)[0]

            # slicework #

            # Text must start where voting new line ends.
            text = self.drive.response.text.split(']<br>', 1)[1]

            # Body must be after that, but before the author signature.
            record['body'] = bs4.BeautifulSoup(text.split('-- <a href=', 1)[0], 'html.parser')

            # Author must be contained within that link.
            author_link = '<a href='+text.split('-- <a href=', 1)[1].split('</a>', 1)[0] + '</a>'
            author = bs4.BeautifulSoup(author_link, 'html.parser').find('a')
            record['username'] = author.text
            record['userlink'] = 'https://www.halfbakery.com' + author.attrs['href']
            # record['created_date'] = // better info in the listing of rss
            # record['modified_date'] = // better info in the listing of rss

            record['links'] = []

            # Links happen to be with rel: nofollow attribute:
            for link in soup.find_all('a', {'rel': 'nofollow'}):
                link_url = link.attrs['href']
                link_data = self.drive.response.text.split(repr(link), 1)[-1].split(']\n\t\t', 1)[0]
                link_text = link_data.split('</nobr><br>', 1)[-1].split(' [<a href=/lr/user/', 1)[0]
                link_sig = '<a href=/lr/user/'+link_data.split('[<a href=/lr/user/', 1)[-1]
                link_username = bs4.BeautifulSoup(link_sig, 'html.parser').find('a').text
                link_userlink = 'https://www.halfbakery.com' + bs4.BeautifulSoup(link_sig, 'html.parser').find('a').attrs['href']
                link_created = link_sig.split('</a>, ', 1)[1].split(', ')[0]
                link_updated = 'last modified ' in link_sig and link_sig.split('last modified ', 1)[-1] or None
                # link_flag_action_link = // can be constructed from known information

                record['links'].append(
                    Link({'-': link_url,
                        'text': link_text,
                        'username': link_username,
                        'userlink': link_userlink,
                        'created_date': link_created,
                        'updated_date': link_updated}
                    )
                )

            # Comments happen to be between last link, and separated by username links.
            if record['links']:
                # if there are links, then comments are after links
                comments_section = self.drive.response.text.split(link_data, 1)[-1]
            else:
                # otherwhise, the comments are after author link
                comments_section = self.drive.response.text.split(author_link, 1)[-1]

            # Comments are separated by user links
            comments_raw = comments_section.split('-- <a href=/lr/user/')

            record['annotations'] = []
            for i, comment in enumerate(comments_raw):
                if i == 0:
                    comment_text = comment.split('\n',1)[-1]
                else:
                    comment_text = '-- <a href=/lr/user/' + comment

                comment_soup = bs4.BeautifulSoup(comment_text, 'html.parser')

                if i > 0:
                    previous_comment_author = comment_soup.find('a')
                    previous_comment_date = comment_text.split('</a>,\n\t\t ',1)[-1].split('<br>\n\t\n\n', 1)[0]
                else:
                    previous_comment_author = None
                    previous_comment_date = None

                comment_content = bs4.BeautifulSoup(comment_text.split('<br>\n\t', 1)[-1].strip(), 'html.parser')

                record['annotations'].append(
                    {
                        'text': comment_content.text.strip(),
                    }
                )

                if i > 0:
                    record['annotations'][i-1].update({
                        'username': previous_comment_author.text,
                        'userlink': 'https://www.halfbakery.com' + previous_comment_author.attrs['href'],
                        'created_date': previous_comment_date
                    })

            record['annotations'] = record['annotations'][:-1]

            self.update(record)


    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _filter(cls,
                drive,
                keyword=None,
                search='',
                filter_type='Q',              # s
                return_properties='iocwvrqh', # d
                offset=0,                     # do
                page_size=100,                # dn
                return_format=1,              # ds
                view_title='metadrive',       # n
                strategy='by_category',
                limit=None,
                ):

        '''
        A method to be used for periodically synchronized. Howver, how it is different from harvest?
        # probably the best way to keep up with the new data, is to track view filtered by "last_modified",

        :strategy: by_category - go through every category
        '''

        # s =
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

        # d =
        return_attributes = {
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

        # ds =
        return_formats = {
         '1': 'table',
         'A': 'RSS 1.0',
         '0': 'unstructured list of names',
         '3': 'group in three columns',
         '9': 'RSS 0.91',
        }


        # if search:
        #     # (search) variant A:
        #     search_url = '{base}?searchexpression={keyword}&ok=OK'.format(
        #         base=__base_url__,
        #         keyword=search or ''
        #     )
        # else:
        #     # (view) variant B:
        #     filter_url = '{base}view/s={s}:d={d}:dh={dh}:dn={dn}:do={do}:ds={ds}:n={n}:i=:t='.format(
        #         base=__base_url__,
        #         s  = filter_type or '',
        #         dn = window_size or '',     # 1..N
        #         dh = '1',
        #         do = window_position or '', # 0..M
        #         ds = return_format or '',
        #         d  = return_properties or '',
        #         n  = view_title or ''       # any name
        #     )

        feed_url = 'https://www.halfbakery.com/view/s=Q:d=iocwvrqh:do={offset}:dn={page_size}:ds=A:n=halfbakery'

        while True:

            drive.get(
                feed_url.format(page_size=page_size, offset=offset)
            )

            soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')
            results = soup.find_all('item')

            for item in results:

                ### Conform to the result to record format '::mindey/topic#halfbakery' ###

                url = item.attrs.get('rdf:about')
                title = item.title.text.rsplit(' (', 1)[0]
                subtitle = item.find('description') and item.find('description').text or None
                votes = utils.meal_votes_parse(item.title.text.rsplit(' (', 1)[-1][:-1])
                created, updated = item.find('dc:coverage').text.split(' - ')
                created_utc = dateparse(created).astimezone(timezone.utc).isoformat()
                updated_utc = dateparse(updated).astimezone(timezone.utc).isoformat()
                author = item.find('dc:creator').text
                category = item.find('dc:subject').text
                placeholder_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=='

                record = dict()
                record['title'] = title
                record['subtitle'] = subtitle
                record.update(votes)
                # record['body'] = None
                record['created_date'] = created_utc
                record['modified_date'] = updated_utc
                record['author'] = {
                    'username': author,
                    'userlink_guess': 'https://www.halfbakery.com/user/{}'.format(
                        author.replace(' ', '_20')),
                }
                record['media'] = {'post_image': placeholder_image}
                record['category'] = category

                # Meta:
                record['-'] = url
                record['@'] = drive.spec + cls.__name__ # or self.__class__.__name__ in other scopes

                #
                # if get_detail=True, call the get()
                # asynchronously in parallel.
                #

                instance = cls(record)
                instance.drive = drive
                yield instance

            if len(results) < page_size:
                break

            offset += page_size

            if limit:
                if offset >= limit:
                    break


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


class Link(Dict):

    @classmethod
    def _filter(cls):
        raise NotImplemented

    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _create(cls):
        raise NotImplemented
