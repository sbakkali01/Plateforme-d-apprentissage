from flask import Blueprint, jsonify, request

import server

exercices_bp = Blueprint("exercices", __name__)


@exercices_bp.route('/all_exercices')
def all_exercices():
    exercices = server.run_query("SELECT id, nom, description, url FROM exercices_table")
    return jsonify([{'id': c[0], 'nom': c[1], 'description': c[2], 'url': c[3]} for c in exercices])


@exercices_bp.route('/search_exercices')
def search_exercices():
    query = request.args.get('query')
    exercices = server.run_query("SELECT id, nom, description, url FROM exercices_table WHERE nom LIKE ?",
                                 ('%' + query + '%',))
    return jsonify([{'id': c[0], 'nom': c[1], 'description': c[2], 'url': c[3]} for c in exercices])
