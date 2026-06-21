from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

FILE_NAME = 'tasks.json'

def load_tasks():
    """Загружает задачи из JSON-файла"""
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    """Сохраняет задачи в JSON-файл"""
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

def get_next_id(tasks):
    """Генерирует следующий ID для новой задачи"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

# Загружаем задачи при старте
tasks = load_tasks()

@app.route('/')
def index():
    """Главная страница со списком задач"""
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Добавляет новую задачу"""
    task_text = request.form.get('task', '').strip()
    if task_text:
        new_task = {
            'id': get_next_id(tasks),
            'text': task_text,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        tasks.append(new_task)
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Удаляет задачу по ID"""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    save_tasks(tasks)
    return redirect('/')

@app.route('/delete_all')
def delete_all():
    """Удаляет все задачи"""
    global tasks
    tasks = []
    save_tasks(tasks)
    return redirect('/')

@app.route('/clear_completed', methods=['POST'])
def clear_completed():
    """Удаляет выполненные задачи"""
    global tasks
    completed_ids = request.form.getlist('completed')
    if completed_ids:
        completed_ids = [int(id) for id in completed_ids]
        tasks = [task for task in tasks if task['id'] not in completed_ids]
        save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Редактирует задачу по ID"""
    # Находим задачу по ID
    task = None
    task_index = -1
    for i, t in enumerate(tasks):
        if t['id'] == task_id:
            task = t
            task_index = i
            break
    
    # Если задача не найдена
    if task is None:
        return "Задача не найдена", 404
    
    # Если пользователь отправил форму (POST)
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        old_text = task['text']
        
        # Проверка: пустое поле
        if new_text == '':
            return render_template('edit.html', 
                                 task=task, 
                                 message="❌ Текст не может быть пустым!",
                                 message_type="error")
        
        # Проверка: текст не изменился
        if new_text == old_text:
            return render_template('edit.html', 
                                 task=task, 
                                 message="ℹ️ Ничего не изменено. Текст остался прежним.",
                                 message_type="info")
        
        # Обновляем задачу
        tasks[task_index]['text'] = new_text
        save_tasks(tasks)
        
        # Перенаправляем на главную
        return redirect('/')
    
    # Если пользователь просто открыл страницу (GET)
    return render_template('edit.html', task=task)
    
if __name__ == '__main__':
    app.run(debug=True)