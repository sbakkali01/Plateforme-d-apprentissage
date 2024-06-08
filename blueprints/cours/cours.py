from flask import Blueprint, jsonify, request

import server
# test
cours_bp = Blueprint("cours", __name__, template_folder="templates")


@cours_bp.route('/all_cours')
def all_cours():
    cours = server.run_query("SELECT id, nom, description, url FROM cours_table")
    return jsonify([{'id': c[0], 'nom': c[1], 'description': c[2], 'url': c[3]} for c in cours])


@cours_bp.route('/search_cours')
def search_cours():
    query = request.args.get('query')
    cours = server.run_query("SELECT id, nom, description, url FROM cours_table WHERE nom LIKE ?", ('%' + query + '%',))
    return jsonify([{'id': c[0], 'nom': c[1], 'description': c[2], 'url': c[3]} for c in cours])
