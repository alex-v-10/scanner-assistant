from modules.flask_app import create_flask_app
from dotenv import load_dotenv
from modules.flask_app.routes import get_search, get_projects
from projects.projects import PROJECTS
from modules.flask_app.set import set_projects_db

load_dotenv()
set_projects_db(PROJECTS)
app = create_flask_app()

# with app.app_context():
#     response = get_projects()
#     print(response.get_json())

if __name__ == '__main__':
    app.run(debug=True)