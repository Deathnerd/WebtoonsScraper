import json
import itertools
from dataclasses import dataclass, field
from json import JSONEncoder
from typing import List

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

galleries = ["https://www.webtoons.com/en/challenge/evil-inc/list?title_no=41853&page={page}".format(page=x) for x in
             range(1, 20)]


@dataclass
class Episode:
    title: str
    number: int
    url: str
    images: List[str] = field(init=False)

    def __post_init__(self):
        print("Getting image urls")
        resp = requests.get(url=self.url)
        if resp.status_code != 200:
            raise Exception("Couldn't get images for Episode {} because of a non-200 return code".format(self.number))
        soup = BeautifulSoup(resp.content, 'html.parser')
        self.images = [x.attrs['data-url'] for x in soup.select('img._images')]
        print("Found {} images".format(len(self.images)))


class EpisodeEncoder(JSONEncoder):

    def default(self, o: Episode):
        return o.__dict__


def get_episodes(gallery_uri: str) -> List[Episode]:
    print("Getting episodes for {}".format(gallery_uri))
    response = requests.get(gallery_uri)
    if response.status_code != 200:
        raise Exception("{} returned a non-200 status code".format(gallery_uri))
    soup = BeautifulSoup(response.content, 'html.parser')
    episodes = soup.select("li[id*=episode]")
    return [Episode(
        get_episode_title(episode),
        get_episode_number(episode),
        get_episode_link(episode)
    ) for episode in episodes]


def get_episode_title(episode: Tag) -> str:
    print("Getting title")
    return episode.select('span.subj>span')[0].text


def get_episode_number(episode: Tag) -> int:
    print("Getting episode number")
    return int(episode.select('span.tx')[0].text.replace("#", ""))


def get_episode_link(episode: Tag) -> str:
    print("Getting link")
    return episode.select('a')[0].attrs['href']


parsed_episodes = list(itertools.chain.from_iterable(get_episodes(gallery) for gallery in galleries))

with open('things.json', 'w') as file:
    json.dump(parsed_episodes, file, indent=4, cls=EpisodeEncoder)
