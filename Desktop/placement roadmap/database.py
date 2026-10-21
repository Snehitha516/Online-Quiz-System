import sqlite3
import os
import bcrypt
import json
from datetime import datetime, timedelta

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'placement_prep.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            college TEXT,
            department TEXT,
            academic_year TEXT,
            cgpa REAL,
            backlogs INTEGER,
            skills TEXT,
            programming_language TEXT,
            target_company TEXT,
            daily_study_time TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 3. Assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            user_id INTEGER PRIMARY KEY,
            coding_score INTEGER,
            aptitude_score INTEGER,
            sql_score INTEGER,
            resume_score INTEGER,
            comm_score INTEGER,
            overall_score INTEGER,
            strong_areas TEXT,
            weak_areas TEXT,
            suggestions TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 4. Roadmaps table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roadmaps (
            user_id INTEGER PRIMARY KEY,
            duration INTEGER,
            roadmap_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 5. Daily tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            task_date TEXT,
            day_number INTEGER,
            tasks_json TEXT,
            completed_tasks_count INTEGER DEFAULT 0,
            total_tasks_count INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, task_date)
        )
    ''')
    
    # 6. User streak table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_streaks (
            user_id PRIMARY KEY,
            streak_count INTEGER DEFAULT 0,
            last_activity_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 7. Notes and revision table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes_revision (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            category TEXT,
            is_bookmarked INTEGER DEFAULT 0,
            revision_interval TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # 8. Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            badge_name TEXT,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, badge_name)
        )
    ''')
    
    conn.commit()
    conn.close()

# User Helpers
def register_user(name, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    try:
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid
        
        # Initialize streak
        cursor.execute(
            "INSERT INTO user_streaks (user_id, streak_count, last_activity_date) VALUES (?, 0, NULL)",
            (user_id,)
        )
        
        conn.commit()
        return {"id": user_id, "name": name, "email": email}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return {"id": user['id'], "name": user['name'], "email": user['email']}
    return None

# Profile Helpers
def save_profile(user_id, profile_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO profiles (user_id, college, department, academic_year, cgpa, backlogs, skills, programming_language, target_company, daily_study_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            college = excluded.college,
            department = excluded.department,
            academic_year = excluded.academic_year,
            cgpa = excluded.cgpa,
            backlogs = excluded.backlogs,
            skills = excluded.skills,
            programming_language = excluded.programming_language,
            target_company = excluded.target_company,
            daily_study_time = excluded.daily_study_time
        """,
        (
            user_id,
            profile_data.get('college'),
            profile_data.get('department'),
            profile_data.get('academic_year'),
            profile_data.get('cgpa'),
            profile_data.get('backlogs'),
            profile_data.get('skills'),
            profile_data.get('programming_language'),
            profile_data.get('target_company'),
            profile_data.get('daily_study_time')
        )
    )
    conn.commit()
    conn.close()

def get_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# Assessment Helpers
def save_assessment(user_id, assessment_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO assessments (user_id, coding_score, aptitude_score, sql_score, resume_score, comm_score, overall_score, strong_areas, weak_areas, suggestions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            coding_score = excluded.coding_score,
            aptitude_score = excluded.aptitude_score,
            sql_score = excluded.sql_score,
            resume_score = excluded.resume_score,
            comm_score = excluded.comm_score,
            overall_score = excluded.overall_score,
            strong_areas = excluded.strong_areas,
            weak_areas = excluded.weak_areas,
            suggestions = excluded.suggestions
        """,
        (
            user_id,
            assessment_data.get('coding_score'),
            assessment_data.get('aptitude_score'),
            assessment_data.get('sql_score'),
            assessment_data.get('resume_score'),
            assessment_data.get('comm_score'),
            assessment_data.get('overall_score'),
            assessment_data.get('strong_areas'),
            assessment_data.get('weak_areas'),
            assessment_data.get('suggestions')
        )
    )
    conn.commit()
    conn.close()

def get_assessment(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

# Roadmap Helpers
def save_roadmap(user_id, duration, roadmap_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO roadmaps (user_id, duration, roadmap_data)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            duration = excluded.duration,
            roadmap_data = excluded.roadmap_data,
            created_at = CURRENT_TIMESTAMP
        """,
        (user_id, duration, json.dumps(roadmap_data))
    )
    conn.commit()
    conn.close()

def get_roadmap(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roadmaps WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['roadmap_data'] = json.loads(data['roadmap_data'])
        return data
    return None

# Tasks Helpers
def get_daily_tasks(user_id, task_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM daily_tasks WHERE user_id = ? AND task_date = ?", (user_id, task_date))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['tasks'] = json.loads(data['tasks_json'])
        return data
    return None

def save_daily_tasks(user_id, task_date, day_number, tasks_list):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total = len(tasks_list)
    completed = len([t for t in tasks_list if t.get('completed')])
    
    cursor.execute(
        """
        INSERT INTO daily_tasks (user_id, task_date, day_number, tasks_json, completed_tasks_count, total_tasks_count)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, task_date) DO UPDATE SET
            tasks_json = excluded.tasks_json,
            completed_tasks_count = excluded.completed_tasks_count,
            total_tasks_count = excluded.total_tasks_count
        """,
        (user_id, task_date, day_number, json.dumps(tasks_list), completed, total)
    )
    conn.commit()
    conn.close()

def update_task_completion(user_id, task_date, task_index, completed):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM daily_tasks WHERE user_id = ? AND task_date = ?", (user_id, task_date))
    row = cursor.fetchone()
    
    if row:
        tasks = json.loads(row['tasks_json'])
        if 0 <= task_index < len(tasks):
            tasks[task_index]['completed'] = completed
            
            total = len(tasks)
            completed_count = len([t for t in tasks if t.get('completed')])
            
            cursor.execute(
                "UPDATE daily_tasks SET tasks_json = ?, completed_tasks_count = ? WHERE user_id = ? AND task_date = ?",
                (json.dumps(tasks), completed_count, user_id, task_date)
            )
            
            # Update streak logic
            if completed_count == total and total > 0:
                # Update last activity date & increment streak
                cursor.execute("SELECT streak_count, last_activity_date FROM user_streaks WHERE user_id = ?", (user_id,))
                streak_row = cursor.fetchone()
                if streak_row:
                    curr_streak = streak_row['streak_count']
                    last_act = streak_row['last_activity_date']
                    
                    if last_act != task_date:
                        new_streak = 1
                        if last_act:
                            last_d = datetime.strptime(last_act, "%Y-%m-%d")
                            curr_d = datetime.strptime(task_date, "%Y-%m-%d")
                            if (curr_d - last_d).days == 1:
                                new_streak = curr_streak + 1
                            elif (curr_d - last_d).days == 0:
                                new_streak = curr_streak
                        
                        cursor.execute(
                            "UPDATE user_streaks SET streak_count = ?, last_activity_date = ? WHERE user_id = ?",
                            (new_streak, task_date, user_id)
                        )
                        
                        # trigger achievement
                        if new_streak >= 15:
                            cursor.execute("INSERT OR IGNORE INTO achievements (user_id, badge_name) VALUES (?, '15-Day Streak')", (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
    conn.close()
    return False

def get_streak(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT streak_count FROM user_streaks WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row['streak_count']
    return 0

# Notes & Revision Helpers
def get_notes(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes_revision WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_note(user_id, title, content, category, revision_interval="1-Day"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes_revision (user_id, title, content, category, revision_interval) VALUES (?, ?, ?, ?, ?)",
        (user_id, title, content, category, revision_interval)
    )
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return note_id

def delete_note(user_id, note_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes_revision WHERE user_id = ? AND id = ?", (user_id, note_id))
    conn.commit()
    conn.close()

def toggle_bookmark_note(user_id, note_id, is_bookmarked):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE notes_revision SET is_bookmarked = ? WHERE user_id = ? AND id = ?",
        (1 if is_bookmarked else 0, user_id, note_id)
    )
    conn.commit()
    conn.close()

# Achievements Helpers
def get_achievements(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT badge_name, unlocked_at FROM achievements WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def unlock_achievement(user_id, badge_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO achievements (user_id, badge_name) VALUES (?, ?)", (user_id, badge_name))
        conn.commit()
    except sqlite3.Error:
        pass
    finally:
        conn.close()

# Helper to automatically verify all schemas are initialized on start
if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
