from modules.flask_app import create_flask_app
from dotenv import load_dotenv
from modules.flask_app.routes import get_search

load_dotenv()
app = create_flask_app()

# with app.app_context():
#     response = get_search()
#     print(response.get_json())

if __name__ == '__main__':
    app.run(debug=True)