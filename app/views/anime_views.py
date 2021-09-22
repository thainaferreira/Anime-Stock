from traitlets.traitlets import validate
from app import exc
from flask import Blueprint, request, jsonify
from app.services.anime_services import AnimeServices
from app.exc.anime_exception import AnimeAlreadExistsError, AnimeNotFoundError

bp_animes = Blueprint('animes', __name__)

@bp_animes.route('/animes', methods=['GET', 'POST'])
def get_create():
    if request.method == 'POST':
        try:
            data = request.json
            error = AnimeServices.validate_keys(data)
            if error:
                return error, 422
            return AnimeServices.create(**data), 201
        # except KeyError as e:
        #     return dict(e), 422
        except AnimeAlreadExistsError as e:
            return e.message, 409
    else:
        animes_list = AnimeServices.get_all()
        return jsonify(animes_list), 200


@bp_animes.route('/animes/<int:anime_id>', methods=['GET'])
def filter(anime_id: int):
    try:
        return AnimeServices.get_by_id(anime_id), 200
    except AnimeNotFoundError as e:
        return e.message, 404


@bp_animes.route('/animes/<int:anime_id>', methods=['PATCH'])
def update(anime_id: int):
    try:
        data = request.json
        error = AnimeServices.validate_keys(data)
        if error:
            return error, 422
        return AnimeServices.update(anime_id, data), 200
    except AnimeNotFoundError as e:
        return e.message, 404


@bp_animes.route('/animes/<int:anime_id>', methods=['DELETE'])
def delete(anime_id: int):
    try:
        return AnimeServices.delete(anime_id), 204
    except AnimeNotFoundError as e:
        return e.message, 404