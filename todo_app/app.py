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

@app.route('/active')
def show_active():
    """Показывает только активные (невыполненные) задачи"""
    active_tasks = [task for task in tasks if not task.get('done', False)]
    return render_template('index.html', tasks=active_tasks)


@app.route('/completed')
def show_completed():
    """Показывает только выполненные задачи"""
    completed_tasks = [task for task in tasks if task.get('done', False)]
    return render_template('index.html', tasks=completed_tasks)

@app.route('/add', methods=['POST'])
def add_task():
    """Добавляет новую задачу"""
    task_text = request.form.get('task', '').strip()
    priority = request.form.get('priority', 'средний')
    if task_text:
        new_task = {
            'id': get_next_id(tasks),
            'text': task_text,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'done': False,       # ← ЗАПЯТАЯ ДОБАВЛЕНА!
            'priority': priority
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


@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    """Переключает статус выполнения задачи"""
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = not task['done']
            save_tasks(tasks)
            break
    return redirect('/')


@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    """Редактирует задачу по ID"""
    task = None
    task_index = -1
    for i, t in enumerate(tasks):
        if t['id'] == task_id:
            task = t
            task_index = i
            break
    
    if task is None:
        return "Задача не найдена", 404
    
    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()
        new_priority = request.form.get('priority', 'средний')  # ← НОВОЕ
        old_text = task['text']
        old_priority = task.get('priority', 'средний')  # ← НОВОЕ
        
        if new_text == '':
            return render_template('edit.html', 
                                 task=task, 
                                 message="❌ Текст не может быть пустым!",
                                 message_type="error")
        
        # Проверка: ничего не изменилось
        if new_text == old_text and new_priority == old_priority:
            return render_template('edit.html', 
                                 task=task, 
                                 message="ℹ️ Ничего не изменено.",
                                 message_type="info")
        
        # Обновляем задачу
        tasks[task_index]['text'] = new_text
        tasks[task_index]['priority'] = new_priority  # ← НОВОЕ
        save_tasks(tasks)
        return redirect('/')
    
    return render_template('edit.html', task=task)


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

@app.route('/by_priority_active')
def by_priority_active():
    """Показывает активные задачи, отсортированные по приоритету"""
    # Берём только невыполненные задачи
    active_tasks = [task for task in tasks if not task['done']]
    
    priority_order = {
        'высокий': 3,
        'средний': 2,
        'низкий': 1
    }
    
    sorted_tasks = sorted(
        active_tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 0),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)    

@app.route('/by_priority')
def by_priority():
    """Сортирует задачи по приоритету (высокий → средний → низкий)"""
    priority_order = {
        'высокий': 3,
        'средний': 2,
        'низкий': 1
    }
    
    sorted_tasks = sorted(
        tasks,
        key=lambda task: priority_order.get(task.get('priority', 'средний'), 0),
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)
@app.route('/search')
def search():
    """Поиск задач по тексту"""
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered_tasks = [
            task for task in tasks 
            if query in task.get('text', '').lower()
        ]
    else:
        filtered_tasks = tasks
    return render_template('index.html', tasks=filtered_tasks, search_query=query)
    
    # ============================================================
# СОРТИРОВКА
# ============================================================

@app.route('/sort/date')
def sort_by_date():
    """Сортировка по дате (новые сверху)"""
    sorted_tasks = sorted(
        tasks, 
        key=lambda t: t.get('created_at', ''), 
        reverse=True
    )
    return render_template('index.html', tasks=sorted_tasks)


@app.route('/sort/status')
def sort_by_status():
    """Сортировка по статусу (сначала активные)"""
    sorted_tasks = sorted(
        tasks, 
        key=lambda t: t.get('done', False)
    )
    return render_template('index.html', tasks=sorted_tasks)


@app.route('/sort/priority')
def sort_by_priority():
    """Сортировка по приоритету (высокий → средний → низкий)"""
    priority_order = {
        'высокий': 1,
        'средний': 2,
        'низкий': 3
    }
    sorted_tasks = sorted(
        tasks,
        key=lambda t: priority_order.get(t.get('priority', 'средний'), 2)
    )
    return render_template('index.html', tasks=sorted_tasks)


@app.route('/sort/alpha')
def sort_by_alpha():
    """Сортировка по алфавиту (А → Я)"""
    sorted_tasks = sorted(
        tasks, 
        key=lambda t: t.get('text', '').lower()
    )
    return render_template('index.html', tasks=sorted_tasks)

if __name__ == '__main__':
    app.run(debug=True)