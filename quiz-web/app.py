from flask import Flask, render_template, request, redirect, session
import csv
import time
import os
import traceback

from app import app

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Random secret key
app.config['SESSION_TYPE'] = 'filesystem'

# Quiz Questions
QUESTIONS = [
    {
        "question": "Which programming language uses 'print()' for output?",
        "options": ["Java", "Python", "C++", "JavaScript"],
        "answer": 1  # Python
    },
    {
        "question": "What is the full form of SQL?",
        "options": ["Structured Query Language", 
                   "Simple Question Language",
                   "System Query Logic",
                   "Standard Question Line"],
        "answer": 0  # Structured Query Language
    },
    {
        "question": "What does CPU stand for?",
        "options": ["Central Processing Unit",
                   "Computer Personal Unit",
                   "Central Process Unit",
                   "Control Processing Unit"],
        "answer": 0  # Central Processing Unit
    },
    {
        "question": "Which device converts digital to analog signals?",
        "options": ["Router", "Switch", "MODEM", "Hub"],
        "answer": 2  # MODEM
    },
    {
        "question": "What is the binary equivalent of decimal 10?",
        "options": ["1010", "1001", "1100", "1111"],
        "answer": 0  # 1010
    },
    {
        "question": "Which is a non-linear data structure?",
        "options": ["Array", "Queue", "Tree", "Linked List"],
        "answer": 2  # Tree
    },
    {
        "question": "What does HTML stand for?",
        "options": ["Hyper Text Markup Language",
                   "High Tech Modern Language",
                   "Hyperlinks and Text Markup Language",
                   "Home Tool Markup Language"],
        "answer": 0  # Hyper Text Markup Language
    },
    {
        "question": "Which protocol is used for secure web communication?",
        "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
        "answer": 2  # HTTPS
    },
    {
        "question": "What is the default port for HTTP?",
        "options": ["80", "443", "21", "25"],
        "answer": 0  # 80
    },
    {
        "question": "Which component manages computer memory?",
        "options": ["ALU", "CU", "RAM", "Operating System"],
        "answer": 3  # Operating System
    },
    {
        "question": "What does OOP stand for?",
        "options": ["Object-Oriented Programming",
                   "Office Operations Protocol",
                   "Open Optical Platform",
                   "Object Output Process"],
        "answer": 0  # Object-Oriented Programming
    }
]
POINTS_PER_QUESTION = 10

def get_rankings():
    rankings = []
    try:
        if not os.path.exists('rankings.csv'):
            return rankings
            
        with open('rankings.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            
            if headers != ['name', 'score', 'time']:
                return rankings
                
            for row in reader:
                if len(row) != 3:
                    continue
                try:
                    rankings.append({
                        'name': row[0],
                        'score': int(row[1]),
                        'time': float(row[2])
                    })
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error reading rankings: {str(e)}")
        traceback.print_exc()
    return rankings

def save_ranking(name, score, time_taken):
    try:
        file_exists = os.path.exists('rankings.csv')
        with open('rankings.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['name', 'score', 'time'])
            writer.writerow([name.strip(), score, time_taken])
    except Exception as e:
        print(f"Error saving ranking: {str(e)}")
        traceback.print_exc()

@app.route('/')
def index():
    try:
        rankings = sorted(get_rankings(),
                         key=lambda x: (-x['score'], x['time']),
                         )[:10]
        return render_template('index.html', rankings=rankings)
    except Exception as e:
        print(f"Index error: {str(e)}")
        traceback.print_exc()
        return render_template('index.html', rankings=[])

@app.route('/start', methods=['POST'])
def start_quiz():
    session.clear()
    session['score'] = 0
    session['correct'] = 0
    session['current_question'] = 0
    session['start_time'] = time.time()
    return redirect('/quiz')

@app.route('/quiz')
def show_quiz():
    try:
        q_index = session.get('current_question', 0)
        if q_index >= len(QUESTIONS):
            return redirect('/results')
            
        question = QUESTIONS[q_index]
        return render_template('quiz.html',
                             question=question,
                             q_number=q_index+1,
                             total=len(QUESTIONS))
    except Exception as e:
        print(f"Quiz error: {str(e)}")
        traceback.print_exc()
        return redirect('/')

@app.route('/answer', methods=['POST'])
def handle_answer():
    try:
        if 'current_question' not in session:
            return redirect('/')
            
        q_index = session['current_question']
        answer = request.form.get('answer', '0')
        
        if q_index < len(QUESTIONS) and answer.isdigit():
            choice = int(answer)
            if 1 <= choice <= 4:
                if choice - 1 == QUESTIONS[q_index]['answer']:
                    session['score'] += POINTS_PER_QUESTION
                    session['correct'] += 1
        session['current_question'] += 1
        return redirect('/quiz')
    except Exception as e:
        print(f"Answer error: {str(e)}")
        traceback.print_exc()
        return redirect('/')

@app.route('/results')
def show_results():
    try:
        if 'score' not in session:
            return redirect('/')
            
        time_taken = round(time.time() - session['start_time'], 2)
        return render_template('results.html',
                             score=session['score'],
                             correct=session['correct'],
                             total=len(QUESTIONS),
                             time=time_taken)
    except Exception as e:
        print(f"Results error: {str(e)}")
        traceback.print_exc()
        return redirect('/')

@app.route('/save', methods=['POST'])
def save_result():
    try:
        name = request.form.get('name', 'Anonymous').strip()
        if not name:
            name = "Anonymous"
        save_ranking(name, session.get('score', 0), session.get('time', 0))
    except Exception as e:
        print(f"Save error: {str(e)}")
        traceback.print_exc()
    finally:
        session.clear()
        return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)