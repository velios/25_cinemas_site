from multiprocessing.dummy import Pool

import requests
from bs4 import BeautifulSoup
import tmdbsimple as tmdb


tmdb.API_KEY = '49f139f62a6320fd0d3f0cc4aee5ee8c'


def make_prefixed_dict(dict, prefix):
    if dict:
        return {prefix + key: value for key, value in dict.items()}


def fetch_tmdb_data(query, prefix='tmdb_'):
    search = tmdb.Search()
    response = search.movie(query=query)
    result_dict = response.get('results', None)
    return make_prefixed_dict(result_dict[0], prefix) if result_dict else {}


def fetch_proxy_list():
    freeproxy_url = 'http://www.freeproxy-list.ru/api/proxy'
    response = requests.get(freeproxy_url, params={'anonymity': 'false', 'token': 'demo'})
    return response.text.split()


def parse_afisha_list():
    afisha_url = 'https://www.afisha.ru/spb/schedule_cinema/'
    raw_afisha_html = requests.get(afisha_url).content

    soup = BeautifulSoup(raw_afisha_html, "html.parser")
    movie_tag_list = soup.find('div', id='schedule').find_all('div', recursive=False)

    movie_data_list = []
    for movie in movie_tag_list:
        movie_content_tag = movie.find('div', {'class': 'm-disp-table'})
        movie_title = movie_content_tag.find('a').text
        movie_link = movie_content_tag.find('a').get('href')
        movie_description = movie_content_tag.find('p').text
        cinema_list = movie.find('tbody').find_all('tr', recursive=False)
        movie_data_list.append({
            'af_title': movie_title,
            'af_description': movie_description,
            'af_cinema_amount': len(cinema_list),
            'af_link': movie_link,
        })
    return movie_data_list


def _fetch_kinopoisk_movie_rating(kinopoisk_movie_id):
    movie_rating_url = 'https://rating.kinopoisk.ru/{id}.xml'.format(id=kinopoisk_movie_id)
    raw_rating_xml = requests.get(movie_rating_url).content

    soup = BeautifulSoup(raw_rating_xml, "xml")
    kp_data = soup.find('kp_rating')
    imdb_data = soup.find('imdb_rating')
    rating_dict = {}
    if kp_data:
        rating_dict.update({
            'rating': kp_data.text,
            'votes': kp_data.attrs['num_vote']
        })
    if imdb_data:
        rating_dict.update({
            'imdb_rating': imdb_data.text,
            'imdb_votes': imdb_data.attrs['num_vote']
        })
    return rating_dict


def fetch_kinopoisk_movie_info(movie_title, prefix='kp_'):
    search_url = 'https://www.kinopoisk.ru/search/suggest'
    search_params = {'q': movie_title, 'topsuggest': 'true', 'ajax': '1'}
    search_response = requests.get(
        search_url,
        params=search_params,
    )
    movie_data_dict = search_response.json()[0]
    movie_kinopoisk_id = movie_data_dict['id']
    movie_data_dict.update(_fetch_kinopoisk_movie_rating(movie_kinopoisk_id))
    return make_prefixed_dict(movie_data_dict, prefix)


def _thread_update_movie_info(movie):
    movie_title = movie['af_title']
    movie.update(fetch_kinopoisk_movie_info(movie_title))
    eng_movie_title = movie['kp_name']
    if eng_movie_title:
        movie_title = eng_movie_title
    movie.update(fetch_tmdb_data(movie_title))
    return movie


def combine_movie_info_to_list_of_dicts(cinema_threshold = 15, return_movie_amount = 10):
    ongoing_movies_list = parse_afisha_list()
    filtered_by_cinema_threshold = [movie for movie in ongoing_movies_list if
                                    movie['af_cinema_amount'] >= cinema_threshold]

    thread_amount = 8
    pool = Pool(thread_amount)
    updated_with_kinopoisk_data = pool.map(_thread_update_movie_info,
                                           filtered_by_cinema_threshold)
    pool.close()
    pool.join()

    processed_movies_list = sorted(updated_with_kinopoisk_data, key=lambda k: k['kp_rating'], reverse=True)
    return processed_movies_list[:return_movie_amount]
