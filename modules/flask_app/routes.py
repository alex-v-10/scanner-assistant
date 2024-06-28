import traceback
from flask import Blueprint, request, jsonify
from .get import get_search_db, get_projects_db
from .set import set_favorite_db, set_hidden_db
from ..utils import get_past_dates

main = Blueprint('main', __name__)

@main.route('/get_search', methods=['GET'])
def get_search():
    dates = get_past_dates(2)
    data = {}
    for date in dates:
        messages_of_date = get_search_db(date)
        if messages_of_date is None:
            return jsonify({'error': 'An error occurred while fetching data for date: ' + date}), 500
        data[date] = messages_of_date
    return jsonify(data)
  
@main.route('/get_projects', methods=['GET'])
def get_projects():
    data = get_projects_db()
    if data is None:
        return jsonify({'error': 'An error occurred while fetching data'}), 500
    return jsonify(data)
  
@main.route('/set_favorite', methods=['POST'])
def set_favorite():
    try:
        data = request.get_json()
        project = data.get('project')
        is_favorite = data.get('is_favorite')
        if project is None or is_favorite is None:
            return jsonify({'error': 'Invalid input'}), 400
        set_favorite_db(project, is_favorite)
        return jsonify({'message': 'Project updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An unexpected error occurred'}), 500
      
@main.route('/set_hidden', methods=['POST'])
def set_hidden():
    try:
        data = request.get_json()
        project = data.get('project')
        is_hidden = data.get('is_hidden')
        if project is None or is_hidden is None:
            return jsonify({'error': 'Invalid input'}), 400
        set_hidden_db(project, is_hidden)
        return jsonify({'message': 'Project updated successfully'}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'An unexpected error occurred'}), 500