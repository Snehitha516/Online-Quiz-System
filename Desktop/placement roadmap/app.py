import os
import json
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
from fpdf import FPDF
import database

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)
CORS(app)

# Ensure database is initialized
database.init_db()

# --- MOCK QUESTIONS AND TOPICS ---
COMPANY_DATA = {
    "TCS": {
        "pattern": "Online Test (Cognitive & Technical) -> Technical Interview -> HR Interview. Focuses heavily on basic aptitude, C/C++ coding, and communication.",
        "questions": ["Explain storage classes in C.", "Difference between structure and union.", "Reverse a string without built-in functions."],
        "aptitude": "Quantitative Aptitude, Logical Reasoning, Verbal Ability",
        "hr": "Tell me about your project. Why TCS?",
        "experiences": "The technical interview was moderate. They asked DBMS, basic C questions, and OOPS concepts. HR was conversational, focused on relocation and career goals."
    },
    "Infosys": {
        "pattern": "InfyTQ or HackWithInfy -> Technical Round -> HR Round. High focus on Python/Java programming, DBMS, and OOPs concepts.",
        "questions": ["Write a program to check if a number is prime.", "What is method overloading vs overriding?", "Explain foreign key constraints."],
        "aptitude": "Mathematical Ability, Logical Reasoning, Pseudocode, Verbal Ability",
        "hr": "Are you willing to relocate? What are your strengths?",
        "experiences": "Infosys focuses heavily on academic concepts. If you know your final year project inside out and basic OOPS/SQL, it is very clearable."
    },
    "Wipro": {
        "pattern": "Wipro NLTH (Aptitude + Coding) -> Technical Interview -> HR. Focuses on general aptitude, coding basics, and general academic knowledge.",
        "questions": ["What is a pointer in C?", "Write a binary search algorithm.", "Explain normalisation in DBMS."],
        "aptitude": "Quantitative, Logical, English, Coding (2 questions)",
        "hr": "Why Wipro? What would you do if you faced a difficult team member?",
        "experiences": "Relatively straightforward. They asked standard data structures and simple algorithms like bubble sort and factorial."
    },
    "Accenture": {
        "pattern": "Cognitive and Technical Assessment -> Coding Assessment -> Communication Assessment -> Interview (Technical + HR combined).",
        "questions": ["What is recursion? Write Fibonacci series.", "Explain inheritance in OOP.", "What is the difference between inner and outer join?"],
        "aptitude": "Critical Reasoning, Problem Solving, Verbal, Abstract Reasoning, Technical (pseudo-code, networking, MS Office, cloud)",
        "hr": "Describe a situation where you worked in a team to solve a problem.",
        "experiences": "The communication round was fully automated in an app. The final interview was mostly behavioral, talking about projects and teamwork."
    },
    "Zoho": {
        "pattern": "Round 1 (Aptitude & C Output) -> Round 2 (Programming - Basic) -> Round 3 (Programming - Advanced) -> Technical HR -> General HR.",
        "questions": ["Print the following pattern...", "Find the matching substring in a string.", "Design a split-wise console application (advanced)."],
        "aptitude": "C output questions, mathematical aptitude, dry-running nested loops",
        "hr": "How do you handle feedback? Why do you want to join Zoho instead of MNCs?",
        "experiences": "Zoho coding tests are intense. They evaluate your clean coding, logical reasoning, and structure. Be ready to write code on paper or in a simple editor without internet access."
    },
    "Amazon": {
        "pattern": "Online Coding Assessment (3 questions) -> 3 Technical Rounds (DSA, System Design) -> Bar Raiser Round. Heavy focus on Leadership Principles and DSA.",
        "questions": ["LRU Cache implementation.", "Merge K Sorted Lists.", "Find the longest path in a binary tree."],
        "aptitude": "Data Structures & Algorithms, System Design, Behavioral questions testing Leadership Principles",
        "hr": "Tell me about a time you failed and what you learned. Give an example of customer obsession.",
        "experiences": "Highly competitive. You must speak out your thought process when solving DSA. Be very familiar with Amazon's 16 Leadership Principles."
    },
    "Google": {
        "pattern": "Online Assessment -> Technical Phone Screen -> 4-5 Onsite Technical Interviews -> Googlyness & Leadership Interview.",
        "questions": ["Implement a search autocomplete system.", "Find shortest path in grid with obstacles.", "Solve dynamic programming on trees."],
        "aptitude": "Advanced Algorithms, Data Structures, Graph Theory, DP, System Design, Googlyness",
        "hr": "How do you handle disagreement with your manager? Tell me about a time you showed initiative.",
        "experiences": "Very rigorous. Questions are open-ended and they check your coding style, efficiency, and edge case handling. Practice writing bug-free code on Google Docs."
    },
    "Microsoft": {
        "pattern": "Online Assessment -> 3-4 Technical Rounds -> Hiring Manager Interview. Focuses on data structures, algorithms, and logical designs.",
        "questions": ["Reverse nodes in k-group.", "Implement a Trie.", "Design a URL shortener backend structure."],
        "aptitude": "DSA, OOPS, System Design, Logical Puzzles",
        "hr": "What technology trend are you most excited about? Why Microsoft?",
        "experiences": "Microsoft interviewers are friendly and helpful. They want to see how you react to hints. Keep your basic concepts (pointers, recursion, trees) extremely clear."
    },
    "Meta": {
        "pattern": "Recruiter Screen -> 1-2 Technical Screens (DSA) -> Onsite (2 DSA, 1 System Design, 1 Behavioral). Focus on clean, bug-free, optimal coding.",
        "questions": ["Subarray Sum Equals K.", "Lowest Common Ancestor of a Binary Tree.", "K Closest Points to Origin."],
        "aptitude": "Algorithms, Scale Architecture, Data Structures",
        "hr": "Tell me about a time you handled a difficult peer disagreement. Why Meta?",
        "experiences": "Meta coding rounds are fast-paced. You need to solve 2 questions in 45 minutes. Optimize for time complexity and write code quickly."
    },
    "Apple": {
        "pattern": "Phone Interview -> Onsite (4-5 rounds of Technical, Domain Specific, and Managers). Heavy focus on OS internals, language design, or hardware depending on team.",
        "questions": ["Reverse a linked list.", "Design an LRU Cache.", "Implement a circular queue."],
        "aptitude": "System Architectures, Low-level programming, Memory Layouts",
        "hr": "Why Apple? Tell me about a project where you paid extreme attention to detail.",
        "experiences": "Very domain-oriented. If you are applying for iOS, they check swift/memory constraints. For systems, they ask pointers, OS kernels, concurrency."
    },
    "Netflix": {
        "pattern": "Recruiter Screen -> Technical Screen -> 2 Onsite Rounds (Technical, System Design, Culture). High focus on Netflix Culture Memo values.",
        "questions": ["Design a video streaming CDN architecture.", "Analyze logs stream for page views.", "Design rating limiters."],
        "aptitude": "Distributed Systems, Scale, Concurrent programming",
        "hr": "How do you align with 'Freedom and Responsibility'? Give an example of choosing long-term efficiency over short-term ease.",
        "experiences": "Very conversational but deeply technical. They focus on how you handle scaling and your maturity. Culture alignment is highly critical here."
    },
    "Oracle": {
        "pattern": "Online Test -> 2-3 Technical Interviews -> HR Round. Focuses on Java, database architectures, SQL, and data structures.",
        "questions": ["Find the second largest element in BST.", "Explain B-Trees vs B+ Trees.", "Write SQL query to find second highest salary."],
        "aptitude": "SQL logic, core Java concepts, general aptitude",
        "hr": "Why database software engineering? What are your career aspirations?",
        "experiences": "Oracle interviews are very theoretical. They ask DBMS normalisation rules, transactions concurrency controls, and Java garbage collectors."
    },
    "Cisco": {
        "pattern": "Written Test -> Technical Rounds -> Managerial Round -> HR Round. High focus on networking concepts (TCP/IP, routing) and basic scripting.",
        "questions": ["Explain DNS resolving process.", "Difference between TCP and UDP headers.", "Check if a binary tree is symmetric."],
        "aptitude": "Networking protocols, IP subnets, routing logic, standard MCQs",
        "hr": "Tell me about a team project. How do you adapt to new technologies?",
        "experiences": "Be very solid with computer networks. Know your routing tables, packet formats, OSI layers, and some basic coding algorithms."
    },
    "Adobe": {
        "pattern": "Online Coding -> Technical Screen -> 2-3 Technical Rounds -> Managerial/HR. Focuses on DSA, design patterns, and C++/Java concepts.",
        "questions": ["Merge two sorted arrays without extra space.", "Design PDF annotations structure.", "Implement custom memory allocator."],
        "aptitude": "Mathematics, logical puzzles, OOP patterns",
        "hr": "Why Adobe? Tell me about a creative solution you built.",
        "experiences": "Interviews check strong problem-solving skills. Puzzles and medium-to-hard DSA questions are common."
    },
    "Salesforce": {
        "pattern": "Coding Test -> 2 Technical Rounds (DSA, OOP) -> System Design -> Hiring Manager. Focuses on cloud scalability, design patterns, and OOP.",
        "questions": ["Design a multitenant database model.", "Validate Binary Search Tree.", "Find intersection of two linked lists."],
        "aptitude": "Object-oriented design, databases structure, scalability puzzles",
        "hr": "What is your experience with cloud systems? Why Salesforce?",
        "experiences": "They ask clean design patterns and standard DSA. Be ready to explain how cloud platforms decouple compute and storage."
    },
    "Uber": {
        "pattern": "Online Assessment -> 2-3 Technical Rounds (DSA, concurrency, architecture) -> HR Bar Raiser. High focus on multi-threaded programming and algorithms.",
        "questions": ["Design a ride-matching system architecture.", "Find word search in grid.", "Implement a Rate Limiter using Redis."],
        "aptitude": "System architecture, high concurrency scale, standard coding puzzles",
        "hr": "How do you handle high pressure environments? Explain a complex technical bug you resolved.",
        "experiences": "Rigorous coding. They expect optimal solutions and clean code structure. Multi-threading questions are very common."
    }
}

STUDY_RESOURCES = {
    "DSA": [
        {"title": "Striver's A2Z DSA Course (YouTube)", "link": "https://www.youtube.com/playlist?list=PLgUwDviBHe0oF65Y-mVJc0TFn0gK0y55M", "type": "Video"},
        {"title": "Love Babbar's DSA Sheet (Resource)", "link": "https://www.geeksforgeeks.org/dsa-sheet-by-love-babbar/", "type": "Practice Sheet"},
        {"title": "Introduction to Algorithms (CLRS Book)", "link": "#", "type": "Book"}
    ],
    "SQL & DBMS": [
        {"title": "Complete SQL BootCamp (Video)", "link": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "type": "Video"},
        {"title": "DBMS Gate Smashing Notes (PDF)", "link": "#", "type": "PDF"},
        {"title": "LeetCode SQL Practice Problems", "link": "https://leetcode.com/studyplan/top-sql-50/", "type": "Practice Website"}
    ],
    "Aptitude": [
        {"title": "IndiaBIX Aptitude Questions", "link": "https://www.indiabix.com/", "type": "Practice Website"},
        {"title": "CareerRide Aptitude Preparation (YouTube)", "link": "https://www.youtube.com/@CareerRide", "type": "Video"}
    ],
    "Operating Systems": [
        {"title": "Gate Smashers OS Lecture Series", "link": "https://www.youtube.com/playlist?list=PLxCzCOWd7aiGz9donHRrE9I3Mwn6XdP8p", "type": "Video"},
        {"title": "OS Lecture Notes - Galvin", "link": "#", "type": "Book"}
    ]
}

# --- PDF GENERATOR CLASS ---
class RoadmapPDF(FPDF):
    def header(self):
        self.set_fill_color(11, 15, 25) # Dark Blue background theme color
        self.rect(0, 0, 210, 297, 'F')
        
        self.set_text_color(99, 102, 241) # Lavender-Indigo color
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'AI PLACEMENT ROADMAP GENERATOR', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(156, 163, 175)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


# --- CONTROLLERS / API ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
        
    user = database.register_user(name, email, password)
    if user:
        # Save user to session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify({"message": "Registration successful", "user": user}), 201
    return jsonify({"error": "Email already registered"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "All fields are required"}), 400
        
    user = database.login_user(email, password)
    if user:
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return jsonify({"message": "Login successful", "user": user}), 200
    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"}), 200

# Get currently logged in user info
@app.route('/api/me', methods=['GET'])
def get_me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"authenticated": False}), 200
    return jsonify({
        "authenticated": True, 
        "user": {
            "id": user_id, 
            "name": session.get('user_name')
        }
    }), 200

# Profile routes
@app.route('/api/profile', methods=['GET', 'POST'])
def handle_profile():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        profile = database.get_profile(user_id)
        if profile:
            return jsonify({"profile": profile}), 200
        return jsonify({"profile": None}), 200
        
    else: # POST
        data = request.get_json()
        database.save_profile(user_id, data)
        return jsonify({"message": "Profile updated successfully"}), 200

# Assessment routes
@app.route('/api/assessment', methods=['GET', 'POST'])
def handle_assessment():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        assessment = database.get_assessment(user_id)
        if assessment:
            return jsonify({"assessment": assessment}), 200
        return jsonify({"assessment": None}), 200
        
    else: # POST
        data = request.get_json()
        # Evaluate automatically to find weak and strong areas
        coding = int(data.get('coding_score', 50))
        aptitude = int(data.get('aptitude_score', 50))
        sql = int(data.get('sql_score', 50))
        resume = int(data.get('resume_score', 50))
        comm = int(data.get('comm_score', 50))
        
        overall = int((coding + aptitude + sql + resume + comm) / 5)
        
        strong = []
        weak = []
        
        scores = [("Coding", coding), ("Aptitude", aptitude), ("SQL & DBMS", sql), ("Resume", resume), ("Communication", comm)]
        for category, score in scores:
            if score >= 75:
                strong.append(category)
            elif score < 60:
                weak.append(category)
                
        if not strong:
            # Fallback
            strong = [max(scores, key=lambda x: x[1])[0]]
        if not weak:
            # Fallback
            weak = [min(scores, key=lambda x: x[1])[0]]
            
        strong_str = ", ".join(strong)
        weak_str = ", ".join(weak)
        
        # Formulate AI suggestions
        suggestions = []
        if coding < 70:
            suggestions.append("Dedicate 2 hours daily to practice Easy-Medium arrays, lists, and trees on LeetCode.")
        if aptitude < 70:
            suggestions.append("Take quantitative tests on IndiaBIX weekly, focusing on Permutations, Probabilities, and Speed calculations.")
        if sql < 70:
            suggestions.append("Practice JOINS, subqueries, and window functions. Revise DBMS Normalization rules.")
        if resume < 75:
            suggestions.append("Format your resume using single-column clean templates. Highlight concrete metrics in your project descriptions.")
        if comm < 75:
            suggestions.append("Practice mock interviews with AI. Speak out loud during coding practice to express your thoughts clearly.")
            
        ai_suggestions = " ".join(suggestions) or "Excellent scores overall! Maintain consistency by practicing advanced coding challenges and system designs."
        
        eval_data = {
            "coding_score": coding,
            "aptitude_score": aptitude,
            "sql_score": sql,
            "resume_score": resume,
            "comm_score": comm,
            "overall_score": overall,
            "strong_areas": strong_str,
            "weak_areas": weak_str,
            "suggestions": ai_suggestions
        }
        
        database.save_assessment(user_id, eval_data)
        # Unlock badge
        if overall >= 85:
            database.unlock_achievement(user_id, "Aptitude Expert")
        if sql >= 85:
            database.unlock_achievement(user_id, "SQL Master")
            
        return jsonify({"message": "Assessment recorded", "assessment": eval_data}), 200

# Roadmap route
@app.route('/api/roadmap', methods=['GET', 'POST'])
def handle_roadmap():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        roadmap = database.get_roadmap(user_id)
        if roadmap:
            return jsonify({"roadmap": roadmap}), 200
        return jsonify({"roadmap": None}), 200
        
    else: # POST
        data = request.get_json()
        duration = int(data.get('duration', 30))
        
        # Fetch profile & assessment to customize
        profile = database.get_profile(user_id) or {}
        assessment = database.get_assessment(user_id) or {}
        
        weak_topics = assessment.get('weak_areas', 'Coding, Aptitude')
        lang = profile.get('programming_language', 'Python')
        company = profile.get('target_company', 'TCS')
        
        roadmap_data = []
        
        # Dynamic schedule generation based on duration
        days_per_period = int(duration / 3)
        
        # Period 1
        roadmap_data.append({
            "period": f"Days 1 to {days_per_period}: Foundation & Core Skills",
            "details": f"Focus on core weaknesses: {weak_topics}. Practice fundamental syntax in {lang} and study DBMS theories.",
            "activities": ["Read basic data structures", "Aptitude Practice (Quantitative)", "SQL JOINs and Group By queries"]
        })
        
        # Period 2
        roadmap_data.append({
            "period": f"Days {days_per_period + 1} to {2 * days_per_period}: Advanced Preparation & Mock Testing",
            "details": f"Transition into standard algorithms, search patterns, and mock interviews tailored for {company}. Revise operating system concepts and resume files.",
            "activities": ["Coding Practice (Medium Recursion/Dynamic Programming)", "Mock Interview practice (OOPS and DBMS questions)", "Resume optimization & project review"]
        })
        
        # Period 3
        roadmap_data.append({
            "period": f"Days {2 * days_per_period + 1} to {duration}: Final Polish & Company-Specific Drills",
            "details": f"Solve previous papers and practice patterns specifically for {company}. Prepare HR question worksheets and take final communication tests.",
            "activities": ["Company-Wise Prep (solve past questions)", "HR Interview mock drills", "1-Day and 1-Week revision planners checks"]
        })
        
        database.save_roadmap(user_id, duration, roadmap_data)
        database.unlock_achievement(user_id, "DSA Beginner")
        
        return jsonify({"message": "Roadmap generated", "roadmap": {"duration": duration, "roadmap_data": roadmap_data}}), 200

# Download Roadmap PDF
@app.route('/api/roadmap/download', methods=['GET'])
def download_roadmap():
    user_id = session.get('user_id') or request.args.get('user_id')
    if not user_id:
        return "Unauthorized", 401
        
    roadmap = database.get_roadmap(user_id)
    profile = database.get_profile(user_id) or {}
    
    if not roadmap:
        return "No roadmap generated yet. Please generate one first.", 404
        
    pdf = RoadmapPDF()
    pdf.add_page()
    pdf.set_text_color(243, 244, 246)
    
    # User Profile Header in PDF
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Preparation Plan for: {session.get('user_name', 'Student')}", 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Target Company: {profile.get('target_company', 'TCS')} | Preferred Language: {profile.get('programming_language', 'Java')}", 0, 1)
    pdf.cell(0, 8, f"Plan Duration: {roadmap['duration']} Days", 0, 1)
    pdf.ln(10)
    
    # Print periods
    for period in roadmap['roadmap_data']:
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(139, 92, 246) # Purple color
        pdf.cell(0, 10, period['period'], 0, 1)
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(209, 213, 219) # Gray text
        pdf.multi_cell(0, 8, period['details'])
        pdf.ln(2)
        
        pdf.set_font('Arial', 'I', 9)
        pdf.set_text_color(34, 211, 238) # Cyan color
        pdf.cell(0, 6, "Daily Tasks Checklist:", 0, 1)
        
        pdf.set_text_color(229, 231, 235)
        for act in period['activities']:
            pdf.cell(10)
            pdf.cell(0, 6, f"- {act}", 0, 1)
        pdf.ln(8)
        
    # Output to local file or return direct stream
    pdf_path = os.path.join(os.path.dirname(__file__), 'temp_roadmap.pdf')
    pdf.output(pdf_path)
    
    return send_file(pdf_path, as_attachment=True, download_name="My_Placement_Roadmap.pdf")

# Tasks API
@app.route('/api/tasks', methods=['GET', 'POST', 'PATCH'])
def handle_tasks():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    if request.method == 'GET':
        tasks_data = database.get_daily_tasks(user_id, today_str)
        if not tasks_data:
            # Let's generate default tasks for today based on roadmap
            roadmap = database.get_roadmap(user_id)
            day_number = 1
            
            # Count how many days of tasks have been recorded to find current day
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM daily_tasks WHERE user_id = ?", (user_id,))
            day_number = cursor.fetchone()[0] + 1
            conn.close()
            
            # Pull checklist from roadmap, if exists
            activities = ["Solve 5 coding problems", "Practice Aptitude questions", "Revise OOPS / SQL basics", "Read current news/HR prep"]
            if roadmap:
                # Find appropriate activities based on current day and duration
                duration = roadmap['duration']
                periods = roadmap['roadmap_data']
                days_per_period = int(duration / 3)
                
                if day_number <= days_per_period:
                    activities = periods[0]['activities']
                elif day_number <= 2 * days_per_period:
                    activities = periods[1]['activities']
                else:
                    activities = periods[2]['activities']
            
            # Map activities to checkboxes
            tasks_list = [{"title": act, "completed": False} for act in activities]
            
            database.save_daily_tasks(user_id, today_str, day_number, tasks_list)
            tasks_data = database.get_daily_tasks(user_id, today_str)
            
        streak = database.get_streak(user_id)
        tasks_data['streak'] = streak
        return jsonify(tasks_data), 200
        
    elif request.method == 'POST':
        # Admin / Manual task replacement
        data = request.get_json()
        tasks_list = data.get('tasks', [])
        day_number = data.get('day_number', 1)
        
        database.save_daily_tasks(user_id, today_str, day_number, tasks_list)
        return jsonify({"message": "Daily tasks updated"}), 200
        
    elif request.method == 'PATCH':
        # Check / uncheck task
        data = request.get_json()
        task_index = int(data.get('task_index'))
        completed = bool(data.get('completed'))
        
        success = database.update_task_completion(user_id, today_str, task_index, completed)
        if success:
            updated_data = database.get_daily_tasks(user_id, today_str)
            updated_data['streak'] = database.get_streak(user_id)
            return jsonify({"message": "Task status updated", "tasks_data": updated_data}), 200
            
        return jsonify({"error": "Failed to update task"}), 400

# Streak Route
@app.route('/api/streak', methods=['GET'])
def get_user_streak():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    streak = database.get_streak(user_id)
    return jsonify({"streak": streak}), 200

# Notes Routes
@app.route('/api/notes', methods=['GET', 'POST', 'DELETE', 'PATCH'])
def handle_notes():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    if request.method == 'GET':
        notes = database.get_notes(user_id)
        return jsonify({"notes": notes}), 200
        
    elif request.method == 'POST':
        data = request.get_json()
        title = data.get('title', 'Untitled Note')
        content = data.get('content', '')
        category = data.get('category', 'General')
        revision_interval = data.get('revision_interval', '1-Day')
        
        note_id = database.add_note(user_id, title, content, category, revision_interval)
        return jsonify({"message": "Note created", "note_id": note_id}), 201
        
    elif request.method == 'DELETE':
        note_id = int(request.args.get('note_id'))
        database.delete_note(user_id, note_id)
        return jsonify({"message": "Note deleted"}), 200
        
    elif request.method == 'PATCH':
        data = request.get_json()
        note_id = int(data.get('note_id'))
        is_bookmarked = bool(data.get('is_bookmarked'))
        
        database.toggle_bookmark_note(user_id, note_id, is_bookmarked)
        return jsonify({"message": "Note bookmark toggled"}), 200

# Achievements API
@app.route('/api/achievements', methods=['GET'])
def get_achievements():
    user_id = session.get('user_id') or request.headers.get('X-User-Id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    achievements = database.get_achievements(user_id)
    return jsonify({"achievements": achievements}), 200

# Company Wise Prep API
@app.route('/api/company-prep/<company_name>', methods=['GET'])
def get_company_prep(company_name):
    if company_name in COMPANY_DATA:
        return jsonify({"company": company_name, "details": COMPANY_DATA[company_name]}), 200
    return jsonify({"error": "Company not found"}), 404

# Study Resources API
@app.route('/api/resources', methods=['GET'])
def get_resources():
    return jsonify({"resources": STUDY_RESOURCES}), 200

# Company Eligibility Checker API
@app.route('/api/company-eligibility', methods=['POST'])
def check_eligibility():
    data = request.get_json()
    cgpa = float(data.get('cgpa', 0.0))
    backlogs = int(data.get('backlogs', 0))
    user_skills = [s.strip().lower() for s in data.get('skills', '').split(',') if s.strip()]
    
    eligibility_requirements = [
        {"name": "TCS", "min_cgpa": 6.0, "max_backlogs": 1, "req_skills": ["c", "c++", "python", "java"]},
        {"name": "Infosys", "min_cgpa": 6.5, "max_backlogs": 0, "req_skills": ["python", "java", "dbms", "sql"]},
        {"name": "Wipro", "min_cgpa": 6.0, "max_backlogs": 0, "req_skills": ["c++", "java", "dsa"]},
        {"name": "Accenture", "min_cgpa": 6.5, "max_backlogs": 1, "req_skills": ["recursion", "oops", "sql"]},
        {"name": "Zoho", "min_cgpa": 5.5, "max_backlogs": 2, "req_skills": ["c", "c++", "java", "logical coding"]},
        {"name": "Amazon", "min_cgpa": 7.5, "max_backlogs": 0, "req_skills": ["dsa", "algorithms", "oops", "system design"]},
        {"name": "Google", "min_cgpa": 8.0, "max_backlogs": 0, "req_skills": ["dsa", "advanced coding", "graphs", "dp"]},
        {"name": "Microsoft", "min_cgpa": 7.5, "max_backlogs": 0, "req_skills": ["dsa", "trie", "oops", "system design"]}
    ]
    
    eligible = []
    not_eligible = []
    
    for comp in eligibility_requirements:
        reasons = []
        if cgpa < comp['min_cgpa']:
            reasons.append(f"CGPA is {cgpa:.2f} (Required: {comp['min_cgpa']})")
        if backlogs > comp['max_backlogs']:
            reasons.append(f"Backlogs is {backlogs} (Max Allowed: {comp['max_backlogs']})")
            
        missing_skills = [sk for sk in comp['req_skills'] if sk not in user_skills]
        
        if not reasons:
            eligible.append({
                "name": comp['name'],
                "required_skills": ", ".join(comp['req_skills']),
                "missing_skills": ", ".join(missing_skills) if missing_skills else "None"
            })
        else:
            not_eligible.append({
                "name": comp['name'],
                "reasons": ", ".join(reasons),
                "required_skills": ", ".join(comp['req_skills'])
            })
            
    return jsonify({
        "eligible": eligible,
        "not_eligible": not_eligible
    }), 200

# Mock AI Resume Analyzer API
@app.route('/api/resume-analyzer', methods=['POST'])
def analyze_resume():
    data = request.get_json()
    resume_text = data.get('resume_text', '')
    
    if not resume_text or len(resume_text.strip()) < 10:
        return jsonify({
            "ats_score": 10,
            "missing_skills": "Core technical skills (like Python, SQL, DSA)",
            "grammar_suggestions": "Make sure your resume text copy contains full sentences.",
            "improvement_tips": "Upload your full resume markdown or paste detailed text describing your college project."
        }), 200
        
    # Evaluate keywords
    keywords = ["python", "java", "sql", "dbms", "javascript", "react", "html", "css", "c++", "c", "dsa", "algorithms", "project", "experience"]
    resume_lower = resume_text.lower()
    
    matched = [k for k in keywords if k in resume_lower]
    score = 40 + int((len(matched) / len(keywords)) * 50)
    if len(resume_text) > 500:
        score += 10
    score = min(score, 100)
    
    missing = [k for k in keywords if k not in matched]
    
    # Fake suggestions
    grammar = "No severe grammatical errors found. Ensure consistent usage of past tense verbs for completed project actions (e.g. 'Created', 'Designed')."
    if "develop" in resume_lower:
        grammar = "Suggest replacing simple verbs like 'developed' with strong action verbs like 'Architected', 'Implemented', or 'Orchestrated'."
        
    tips = [
        "Incorporate metric-driven bullet points (e.g. 'Optimized algorithm speed by 25%').",
        "Add a dedicated 'Key Skills' section grouped logically into Languages, Frameworks, and Tools.",
        "Ensure contact information (LinkedIn, GitHub) links are visible."
    ]
    
    return jsonify({
        "ats_score": score,
        "missing_skills": ", ".join(missing) if missing else "None! Excellent coverage.",
        "grammar_suggestions": grammar,
        "improvement_tips": " ".join(tips)
    }), 200

# Mock AI Chat Assistant API
@app.route('/api/chat-assistant', methods=['POST'])
def chat_assistant():
    data = request.get_json()
    message = data.get('message', '').strip().lower()
    
    if not message:
        return jsonify({"reply": "Hello! How can I help you today with your placement preparation?"}), 200
        
    # Intelligent response selector
    if "stack" in message:
        reply = (
            "### What is a Stack?\n\n"
            "A **Stack** is a linear data structure that follows the **LIFO (Last In First Out)** principle. "
            "The element added last is the first to be removed. Think of a pile of plates: you place the newest plate on top, and you remove the top plate first.\n\n"
            "#### Core Operations:\n"
            "- `push(x)`: Adds an element `x` to the top. (O(1) time)\n"
            "- `pop()`: Removes the element from the top. (O(1) time)\n"
            "- `peek()` or `top()`: Returns the top element without removing it. (O(1) time)\n"
            "- `isEmpty()`: Checks if the stack is empty. (O(1) time)\n\n"
            "#### Implementation Example (Python):\n"
            "```python\n"
            "class Stack:\n"
            "    def __init__(self):\n"
            "        self.stack = []\n"
            "    def push(self, val):\n"
            "        self.stack.append(val)\n"
            "    def pop(self):\n"
            "        return self.stack.pop() if not self.isEmpty() else 'Stack Empty'\n"
            "    def isEmpty(self):\n"
            "        return len(self.stack) == 0\n"
            "```"
        )
    elif "dbms" in message or "database" in message:
        reply = (
            "### What is DBMS?\n\n"
            "**Database Management System (DBMS)** is software used to store, manage, and retrieve user data while keeping optimal security measures. "
            "It acts as an interface between the application and the database files.\n\n"
            "#### Types of DBMS:\n"
            "1. **Relational DBMS (RDBMS)**: Data is stored in structured tables with rows and columns (e.g. MySQL, PostgreSQL, SQLite). Uses SQL.\n"
            "2. **NoSQL DBMS**: Non-relational, schema-less. Stores data in Key-Value pairs, Documents, Columns, or Graphs (e.g., MongoDB, Redis).\n\n"
            "#### Crucial Interview Topics:\n"
            "- **ACID Properties**: Atomicity, Consistency, Isolation, Durability. Ensuring transactions execute reliably.\n"
            "- **Normalization**: Organizing schemas to reduce data redundancy (1NF, 2NF, 3NF, BCNF).\n"
            "- **Indexing**: Enhancing speed of retrieval queries using B-Trees or Hash indexes."
        )
    elif "sql" in message or "join" in message:
        reply = (
            "### SQL Joins Cheat Sheet\n\n"
            "SQL Joins are used to combine rows from two or more tables based on a related column.\n\n"
            "- **INNER JOIN**: Returns records that have matching values in both tables.\n"
            "- **LEFT (OUTER) JOIN**: Returns all records from the left table, and matched records from the right table. (If no match, returns NULL on the right).\n"
            "- **RIGHT (OUTER) JOIN**: Returns all records from the right table, and matched records from the left.\n"
            "- **FULL (OUTER) JOIN**: Returns all records when there is a match in either left or right table.\n\n"
            "#### Sample Query:\n"
            "```sql\n"
            "SELECT employees.name, departments.dept_name\n"
            "FROM employees\n"
            "INNER JOIN departments \n"
            "ON employees.dept_id = departments.id;\n"
            "```"
        )
    elif "oops" in message or "object oriented" in message:
        reply = (
            "### The 4 Pillars of OOPs\n\n"
            "Object-Oriented Programming (OOPs) is a paradigm that uses **Classes** and **Objects** to structure code. The 4 main pillars are:\n\n"
            "1. **Inheritance**: Subclasses inherit properties and actions from parent classes, facilitating code reuse. (e.g., `class Dog(Animal)`)\n"
            "2. **Polymorphism**: The ability of a message or function to be displayed in more than one form. Achieved via **Method Overloading** (compile-time) and **Method Overriding** (runtime).\n"
            "3. **Encapsulation**: Wrapping data variables and code methods together into a single unit (class), hiding direct field access using private/protected specifiers.\n"
            "4. **Abstraction**: Hiding internal implementation complexities and showing only functional outer interfaces to users. Achieved via Abstract Classes or Interfaces."
        )
    elif "coding" in message or "dsa" in message:
        reply = (
            "### Strategy for DSA Preparation\n\n"
            "To crack top technical rounds, prepare in this sequence:\n"
            "1. Learn one coding language well (**C++ STL** or **Java Collections** or **Python Standard Lib**).\n"
            "2. Master basic structures: Arrays, Strings, Matrices, Lists.\n"
            "3. Practice recursion & sorting: Binary Search, Merge/Quick Sort.\n"
            "4. Intermediate: Stacks, Queues, HashMaps, Trees (DFS/BFS traversal).\n"
            "5. Advanced: Graphs (BFS/DFS, Dijkstra), Dynamic Programming (Knapsack, LCS).\n\n"
            "Try to solve at least **150-200** curated standard questions on LeetCode/GeeksforGeeks to cover all common patterns."
        )
    else:
        reply = (
            "That's a great question! For placement preparation, make sure you know the fundamentals of data structures (arrays, trees), basic databases (SQL join structures, normalisation), and your final year project details. Let me know if you want me to explain any specific concept like a **Stack**, **OOPs pillars**, or **DBMS basics**!"
        )
        
    return jsonify({"reply": reply}), 200

# Mock AI Mock Interview API
@app.route('/api/mock-interview', methods=['POST'])
def start_interview():
    data = request.get_json()
    stage = data.get('stage', 'start') # 'start', 'respond'
    topic = data.get('topic', 'OOPS')
    q_index = int(data.get('q_index', 0))
    user_response = data.get('response', '')
    
    technical_questions = {
        "OOPS": [
            "Explain the difference between interface and abstract class.",
            "What is multiple inheritance? Does Java support it?",
            "What is method overriding and how does it differ from method overloading?"
        ],
        "DBMS": [
            "What are ACID properties? Explain each briefly.",
            "What is a primary key, foreign key, and unique key?",
            "What is database indexing and what are the drawbacks?"
        ],
        "SQL": [
            "What is the difference between WHERE and HAVING clause?",
            "Explain inner join, left join, and self join.",
            "What is a subquery? When should we use it?"
        ],
        "OS": [
            "What is paging? What is virtual memory?",
            "Explain process vs thread. What is context switching?",
            "What is a deadlock? What are the four conditions for deadlocks?"
        ],
        "CN": [
            "Explain the layers of the OSI model.",
            "What is the difference between TCP and UDP?",
            "What happens when you type a URL in the browser?"
        ],
        "DSA": [
            "Explain binary search algorithm. What is its time complexity?",
            "What is a binary search tree (BST) and how is it used?",
            "Explain the difference between BFS and DFS."
        ],
        "HR": [
            "Tell me about yourself.",
            "Why should we hire you? What are your weaknesses?",
            "Tell me about a time you had a conflict in a group project. How did you resolve it?"
        ]
    }
    
    questions = technical_questions.get(topic, technical_questions["OOPS"])
    
    if stage == 'start':
        return jsonify({
            "question": questions[0],
            "q_index": 0,
            "next_stage": "respond"
        }), 200
        
    elif stage == 'respond':
        # Analyze response and provide scores
        char_count = len(user_response.strip())
        
        # Simple keywords count
        technical_keywords = {
            "OOPS": ["inherit", "extend", "abstract", "implement", "hide", "private", "overload", "override", "virtual", "compile", "run"],
            "DBMS": ["atomicity", "consistency", "isolation", "durability", "transaction", "uniqueness", "null", "index", "b-tree"],
            "SQL": ["row", "filter", "aggregate", "group by", "combine", "matching", "table", "nested", "performance"],
            "OS": ["memory", "disk", "cpu", "execution", "register", "mutual exclusion", "hold and wait", "preemption", "segmentation"],
            "CN": ["application", "transport", "network", "physical", "handshake", "packet", "connection", "dns", "ip"],
            "DSA": ["divide", "conquer", "sorted", "middle", "left", "right", "tree", "node", "queue", "stack", "recursion"],
            "HR": ["learn", "improve", "team", "project", "work", "challenge", "collaborate", "solve", "ambition"]
        }
        
        keywords = technical_keywords.get(topic, [])
        matches = [kw for kw in keywords if kw in user_response.lower()]
        
        # Grade performance
        if char_count < 15:
            tech_score = 30
            comm_score = 30
            confidence = "Low"
            feedback = "The answer is too brief. Try to explain concepts in detail, provide examples, and structure your explanation logically."
        else:
            tech_score = min(50 + len(matches) * 10, 100)
            comm_score = min(60 + int(char_count / 15), 100)
            confidence = "High" if len(matches) >= 3 else "Medium"
            
            feedback = "Great effort! You touched on key points. For absolute clarity, try referencing syntax examples or standard use-cases."
            if len(matches) < 2:
                feedback += " Try incorporating key terminology like: " + ", ".join(keywords[:3]) + "."
                
        # Advance question or finish
        next_index = q_index + 1
        has_next = next_index < len(questions)
        
        response_payload = {
            "evaluation": {
                "tech_score": tech_score,
                "comm_score": comm_score,
                "confidence_level": confidence,
                "suggestions": feedback
            },
            "has_next": has_next
        }
        
        if has_next:
            response_payload["next_question"] = questions[next_index]
            response_payload["q_index"] = next_index
        else:
            # Complete assessment
            database.unlock_achievement(user_id, "DSA Beginner") # Unlock simple badge
            
        return jsonify(response_payload), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
