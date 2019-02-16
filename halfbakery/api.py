# This includes the methods available to items of the source for user with session.
import bs4
import feedparser
import metawiki
from dateutil.parser import parse as dateparse
from datetime import timezone


class Topic(dict):

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    # def __init__(self, idea_url, session):
    #     self.session = session
    #     self.idea_url = idea_url
    #     if '://www.halfbakery.com/lr/' not in self.idea_url:
    #         self.idea_url = self.idea_url.replace(
    #             '://www.halfbakery.com/',
    #             '://www.halfbakery.com/lr/'
    #         )

    def _get(self):
        raise NotImplemented

    @classmethod
    def _filter(
            cls,
            query=None,
            session=None,
            page_size=100,
            offset=0,
            limit=None,
            get_detail=False):
        '''
        -> Download all titles, descriptions and dates.
        -> Create if not exists, update if exists. (call sync_one if updated)
        -> produce (yield) items with *, +, -.
        '''

        feed_url = 'http://www.halfbakery.com/lr/view/fxc=230:s=R:d=iwqhvroc:do={offset}:dn={page_size}:ds=A:n=tiny:t=halfbakery'

        while True:

            results = feedparser.parse(feed_url.format(
                page_size=page_size,
                offset=offset
            ))['entries']

            for result in results:

                ### Conform to the result to record format '::mindey/topic#halfbakery' ###

                record = {}
                created, updated = result['dc_coverage'].split(' - ')
                created_utc = dateparse(created).astimezone(timezone.utc).isoformat()
                updated_utc = dateparse(updated).astimezone(timezone.utc).isoformat()

                record['author'] = {
                    'date': created_utc,
                    'userlink': 'http://www.halfbakery.com/user/{}'.format(result['author'].replace(' ', '_20')),
                    'username': result['author'],
                    'last_modified': updated_utc
                }
                record['category'] = result['tags'][0]['term']

                def title_vote_splitter(title_info):

                    title = title_info.rsplit(' (', 1)[0]

                    meal_votes = title_info.rsplit(' (', 1)[-1][:-1]
                    meal, votes = meal_votes.split(': ')
                    meal = float(meal)

                    if ',' in votes:
                        pos, neg = votes.split(', ')
                    else:
                        if votes.startswith('+'):
                            pos, neg = int(votes[1:]), 0
                        elif votes.startswith('-'):
                            pos, neg = 0, int(votes[1:])
                        else:
                            pos, neg = 0, 0

                    return {'title': title,
                            'meal': meal,
                            'votes': {'positive': pos, 'negative': neg}}

                title_details = title_vote_splitter(result['title'])
                record['title'] = title_details['title']
                record['votes'] = title_details['votes']
                record['meal'] = title_details['meal']

                if session:
                    record['+'] = metawiki.name_to_url(session.metaname)
                record['-'] = result['id']

                #
                # if get_detail=True, call the get()
                # asynchronously in parallel.
                #
                yield cls(record)

            if len(results) < page_size:
                break

            offset += page_size

            if limit:
                if offset >= limit:
                    break

    def _update(self, value: int):
        '''
        Changes your vote on an idea. Value can be betwee -1, 0, 1.
        '''
        page = self.session.get(self.idea_url)
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
            self.session.get(
                self.idea_url,
                params={
                    'op': 'nay',
                    'sig': sig
                }
            )

        if value == 0:
            self.session.get(
                self.idea_url,
                params={
                    'op': 'unvote',
                    'sig': sig
                }
            )
        if value == 1:
            self.session.get(
                self.idea_url,
                params={
                    'op': 'aye',
                    'sig': sig
                }
            )

    def add_comment(self, text):
        '''
        Creates an annotation to an idea.
        '''
        raise NotImplemented


class Comment(dict):

    def _get(self):
        raise NotImplemented

    @classmethod
    def _filter(cls):
        raise NotImplemented

    def _update(self, anno_url, text):
        '''
        Edits own annotation to an idea.
        '''
        raise NotImplemented
