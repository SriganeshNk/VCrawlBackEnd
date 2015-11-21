from flask import jsonify, request

from . import api
from ..models.sample import Sample
from ..schemas.sample import sample_schema, samples_schema


@api.route('/samples', methods=['GET'])
def get_samples():
    pass


@api.route('/samples/<int:id>', methods=['GET'])
def get_sample(id):
    pass


@api.route('/samples', methods=['POST'])
def create_sample():
    pass


@api.route('/samples/<int:id>', methods=['PUT'])
def update_sample(id):
    pass


@api.route('/samples/<int:id>', methods=['DELETE'])
def delete_sample(id):
    pass
