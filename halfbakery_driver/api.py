import os
import bs4
import yaml
from metatype import Dict
from halfbakery_driver import __base_url__

from dateutil.parser import parse as dateparse
from datetime import timezone
import datetime

from halfbakery_driver import utils
from tqdm import tqdm
import time
import random
from metadrive.config import DATA_DIR
from metaform import List


# list directory by file modification time
from pathlib import Path
listdir = lambda dirpath: [
    str(fname) for fname in
    sorted(Path(dirpath).iterdir(),
    key=lambda f: f.stat().st_mtime)]


class User(Dict):

    @classmethod
    def _sync(cls, drive, scan='last', pause=0., recency_threshold=86400, standard_deviation=1.):
        DAYS_OLD = 10

        for user in tqdm(cls._filter(drive=drive), desc='Users'):

            local_modtime = user.local_modtime()

            if scan == 'last':
                local_modtime = user.local_modtime()
                if local_modtime is not None:
                    if (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(local_modtime)) < datetime.timedelta(seconds=int(DAYS_OLD*recency_threshold + standard_deviation*recency_threshold*random.random())):
                        continue

            user._refresh()
            user.save()
            time.sleep(pause)

    def _refresh(self):

        if self.get('-') is not None:

            url = self['-']
            self.drive.get(url)
            soup = bs4.BeautifulSoup(self.drive.response.content, 'html.parser')

            record = dict()
            title = soup.find('title')
            first_idea = soup.find('a', {'class': ['oldidea', 'newidea']})
            random_link = soup.find('a', text='random')

            if first_idea is not None:
                bio_details = bs4.BeautifulSoup(repr(soup.find('body')).split(repr(title))[-1].split(repr(first_idea), 1)[0], 'html.parser')
            else:
                bio_details = bs4.BeautifulSoup(repr(soup.find('body')).split(repr(title))[-1].split(repr(random_link), 1)[0], 'html.parser')

            record['username'] = title.text

            record['bio'] = bio_details.text.rsplit('[', 1)[0].strip()
            if record['bio'].startswith(record['username']):
                record['bio'] = record['bio'][len(record['username']):]

            record['ideas'] = [{
                'title': idea.text,
                '-': 'https://www.halfbakery.com'+idea.attrs['href'].split('#', 1)[0]}
                for idea in soup.find_all('a', {'class': ['oldidea', 'newidea']})]

            dates = bio_details.text.rsplit('[', 1)[-1].replace(']','').strip()

            if ', last modified ' in dates:
                created, updated = dates.split(', last modified ', 1)
            else:
                created = dates
                updated = dates

            created_utc = dateparse(created).astimezone(timezone.utc).isoformat()
            updated_utc = dateparse(updated).astimezone(timezone.utc).isoformat()

            record['user_updated_date'] = updated_utc
            record['created_date'] = created_utc
            record['updated_date'] = datetime.datetime.utcnow().astimezone(timezone.utc).isoformat()
            self.update(record)

    @classmethod
    def _filter(cls, drive, keyword=None):
        # Go over all ideas, to capture unique user links

        # Idea._sync(drive=drive)

        userlinks = list()

        for idea in Idea._filter(drive=drive, from_disk=True):

            newlinks = set()

            if idea.get('userlink'):
                newlinks.add(idea['userlink'])

            if idea.get('links') is not None:
                for link in idea['links']:
                    newlinks.add(link['userlink'])

            if idea.get('annotations') is not None:
                for anno in idea['annotations']:
                    newlinks.add(anno['userlink'])

            for link in newlinks:
                if link not in userlinks:
                    userlinks.append(link)
                    record = {'-': link}
                    record['@'] = drive.spec + cls.__name__
                    instance = cls(record)
                    instance.drive = drive
                    yield instance

        del userlinks

    @classmethod
    def _get(cls):
        raise NotImplemented

    @classmethod
    def _create(cls):
        raise NotImplemented


class Category(Dict):

    @classmethod
    def _sync(cls, drive, scan='last', pause=0., recency_threshold=86400, standard_deviation=1.):
        '''
        Synchronizes source with local:
            Gets the latest objects in stream, until the last object with identical modification date.

        :scan: 'last' / 'full' -- a condition to stop, or just get all data from source.
        '''

        for item in tqdm(cls._filter(drive=drive), desc='Categories'):


            if scan == 'last':
                local_modtime = item.local_modtime()
                if local_modtime is not None:
                    if (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(local_modtime)) < datetime.timedelta(seconds=int(recency_threshold + standard_deviation*recency_threshold*random.random())):
                        continue

            item._refresh()
            item.save()
            time.sleep(pause)


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


class Idea(Dict):

    @classmethod
    def _sync(cls, drive, scan='last', offset=0, pause=0.):
        '''
        Synchronizes source with local:
            Gets the latest objects in stream, until the last object with identical modification date.

        :scan: 'last' / 'full' -- a condition to stop, or just get all data from source.
        '''

        for item in tqdm(cls._filter(drive=drive, offset=offset), desc='Ideas'):

            local_modtime = item.local_modtime()

            if scan == 'last':
                if local_modtime is not None:
                    if local_modtime == item.object_modtime():
                        break

            elif scan == 'full':
                if local_modtime is not None:
                    if local_modtime == item.object_modtime():
                        continue

            item._refresh()
            item.save()

            time.sleep(pause)


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
            record['body'] = bs4.BeautifulSoup(text.split('-- <a href=', 1)[0], 'html.parser').text

            # Author must be contained within that link.
            author_link = '<a href='+text.split('-- <a href=', 1)[1].split('</a>', 1)[0] + '</a>'
            author = bs4.BeautifulSoup(author_link, 'html.parser').find('a')
            record['username'] = author.text
            record['userlink'] = 'https://www.halfbakery.com' + author.attrs['href']
            # record['created_date'] = // better info in the listing of rss
            # record['updated_date'] = // better info in the listing of rss

            record['links'] = []
            record['votes'] = utils.raw_votes_parse(bs4.BeautifulSoup(repr(soup).split('<nobr>', 1)[-1].split('[', 1)[0], 'html.parser').text.strip().replace('\n', ' '))


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
                    # Link(
                    {'-': link_url,
                     'text': link_text,
                     'username': link_username,
                     'userlink': link_userlink,
                     'created_date': link_created,
                     'updated_date': link_updated}
                    # )
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
                limit=None,
                from_disk=False,
                ):


        if from_disk:

            directory = os.path.join(DATA_DIR, drive.drive_id, cls.__name__)

            for filename in listdir(directory):

                idea = yaml.load(
                    open(
                        os.path.join(directory, filename)).read(), Loader=yaml.Loader)

                yield cls(idea)

            return


        feed_url = 'https://www.halfbakery.com/view/s=Q:d=iocwvrqh:do={offset}:dn={page_size}:ds=A:n=halfbakery'

        while True:

            drive.get(
                feed_url.format(page_size=page_size, offset=offset)
            )

            soup = bs4.BeautifulSoup(drive.response.content, 'html.parser')
            results = soup.find_all('item')

            for item in results:

                # DATA
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

                # RECORD
                record = dict()
                record['-'] = url
                record['@'] = drive.spec + cls.__name__
                record['title'] = title
                record['subtitle'] = subtitle
                record.update(votes)
                record['created_date'] = created_utc
                record['updated_date'] = updated_utc
                record['author'] = {
                    'username': author,
                    'userlink_guess': 'https://www.halfbakery.com/user/{}'.format(
                        author.replace(' ', '_20')),
                }
                record['media'] = {'post_image': placeholder_image}
                record['category'] = category

                # OBJECT
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

    @property
    def annotations(self):

        if not self.get('annotations'):
            results = List([])
        else:
            results = List([Annotation(item)
                for item in self['annotations']])

        # setattr(results, 'create', Annotation._create)
        return results

    def add_annotation(self, value):
        raise NotImplemented


    @property
    def links(self):
        if not self.get('links'):
            return []

        return [Link(item)
                for item in self['links']]

    def add_link(self, value):
        raise NotImplemented

    @property
    def votes(self):
        return self.get('votes')

    def set_vote(self, value):
        '''
        Changes your vote on an idea. Value can be betwee -1, 0, 1.
        '''

        url = self.get('-')

        if url is not None:
            if 'halfbakery.com/lr/' not in url:
                url = url.replace('halfbakery.com/', 'halfbakery.com/lr/')
            self.drive.get(url)
            page = self.drive.response
        else:
            raise Exception("Could not retrieve idea page.")

        if page.ok:
            soup = bs4.BeautifulSoup(page.content, 'html.parser')
            sig = soup.find('input', {'name': 'sig'})
            if sig:
                sig = sig.attrs['value']
            else:
                raise Exception("Log in to vote.")
        else:
            raise Exception("Log in to vote.")

        if value == -1:
            self.drive.get(
                url,
                params={
                    'op': 'nay',
                    'sig': sig
                }
            )

        if value == 0:
            self.drive.get(
                url,
                params={
                    'op': 'unvote',
                    'sig': sig
                }
            )
        if value == 1:
            self.drive.get(
                url,
                params={
                    'op': 'aye',
                    'sig': sig
                }
            )

        self._refresh()
        self.save()
