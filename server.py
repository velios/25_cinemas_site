from argparse import ArgumentParser

from flask import Flask, render_template
from flask_caching import Cache
from flask_restful import Resource, Api

from cinemas import combine_movie_info_to_list_of_dicts


app = Flask(__name__)
api = Api(app)
cache = Cache(app, config={'CACHE_TYPE': 'filesystem',
                           'CACHE_DIR': 'cache',
                           'CACHE_THRESHOLD': 500})


def fetch_cmd_arguments():
    parser_description = 'Run flask server'
    parser = ArgumentParser(description=parser_description)
    parser.add_argument('-d', '--debug_mode',
                        help='Run in debug mode',
                        action='store_true')
    return parser.parse_args()


class MoviesSimple(Resource):
    def get(self):
        movie_data_list = cached_movie_data()
        return {
            'length': len(movie_data_list),
            'results': movie_data_list
        }


class MoviesFiltered(Resource):
    def get(self, result_amount, cinemas_amount):
        movie_data_list = combine_movie_info_to_list_of_dicts(cinema_threshold=cinemas_amount,
                                                              return_movie_amount=result_amount)
        return {
            'length': len(movie_data_list),
            'results': movie_data_list
        }


@cache.cached(timeout=60*60*12, key_prefix='movie_data')
def cached_movie_data():
    return combine_movie_info_to_list_of_dicts(cinema_threshold=12)


@app.route('/')
@cache.cached(timeout=60)
def films_list():
    movie_data_list = cached_movie_data()
    return render_template('films_list.html',
                           movie_data_list = movie_data_list,)


@app.route('/api')
def api_page():
    return render_template('api.html')

api.add_resource(MoviesSimple, '/api/movies')
api.add_resource(MoviesFiltered, '/api/movies/<int:result_amount>/cinemas/<int:cinemas_amount>')

if __name__ == "__main__":
    cmd_args = fetch_cmd_arguments()
    if cmd_args.debug_mode:
        app.config['DEBUG'] = True
    app.run()
