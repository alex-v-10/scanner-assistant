import sqlite3
import traceback
from ..const import DATABASE


def set_projects_db(projects):   
    for project in projects:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            project_name = project['project']
            cursor.execute('SELECT project FROM projects WHERE project = ?', (project_name,))
            result = cursor.fetchone()
            if result is None:
                cursor.execute('''
                    INSERT INTO projects (project, is_favorite, is_hidden)
                    VALUES (?, 0, 0)
                ''', (project_name,))
            conn.commit()
        except Exception as e:
            traceback.print_exc() 
            print(f"An unexpected error occurred: {e}")
        finally:
            cursor.close()
            conn.close()
            
def set_favorite_db(project, is_favorite):   
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        is_favorite_value = 1 if is_favorite else 0
        cursor.execute('''
            UPDATE projects
            SET is_favorite = ?
            WHERE project = ?
        ''', (is_favorite_value, project))
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        
def set_hidden_db(project, is_hidden):   
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        is_hidden_value = 1 if is_hidden else 0
        cursor.execute('''
            UPDATE projects
            SET is_hidden = ?
            WHERE project = ?
        ''', (is_hidden_value, project))
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()