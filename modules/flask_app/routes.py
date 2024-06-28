from flask import Blueprint, jsonify
from .get import get_searched_messages
from ..utils import get_past_dates

main = Blueprint('main', __name__)

@main.route('/search', methods=['GET'])
def get_search():
    dates = get_past_dates(2)
    data = {}
    for date in dates:
        messages_of_date = get_searched_messages(date)
        if messages_of_date is None:
            return jsonify({'error': 'An error occurred while fetching data for date: ' + date}), 500
        if messages_of_date:
           data[date] = messages_of_date
    return jsonify(data)