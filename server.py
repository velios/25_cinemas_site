from argparse import ArgumentParser

from flask import Flask, render_template
from flask_caching import Cache

from cinemas import combine_movie_info_to_list_of_dicts


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem',
                           'CACHE_DIR': 'cache',
                           'CACHE_THRESHOLD': 500})


def make_cmd_arguments_parser():
    parser_description = 'Run flask server'
    parser = ArgumentParser(description=parser_description)
    parser.add_argument('-d', '--debug_mode',
                        help='Run in debug mode',
                        action='store_true')
    return parser


@cache.cached(timeout=86400, key_prefix='movie_data')
def cached_movie_data():
    return combine_movie_info_to_list_of_dicts()


@app.route('/')
@cache.cached(timeout=60)
def films_list():
    movie_data_list = cached_movie_data()
    return render_template('films_list.html', movie_data_list = movie_data_list)

if __name__ == "__main__":
    cmd_args_parser = make_cmd_arguments_parser()
    cmd_args = cmd_args_parser.parse_args()
    if cmd_args.debug_mode:
        app.config['DEBUG'] = True
    app.run()
