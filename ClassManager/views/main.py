from django.shortcuts import render
from ClassManager.models import Student, Task, Work


def get_base_context(pagetitle=''):
    return {
        'pagetitle': pagetitle,
        'menu': {
            '/': 'Главная',
            # '.1': 'Журнал',
            # '.2': 'Some more'
        },
        'student_menu': {
            '/student/works/': 'Работы',
            '/student/profile/': 'Профиль',
        },
        'teacher_menu': {
            '/teacher/tasks/': 'Задания',
            '/teacher/students/': 'Студенты',
            '/teacher/groups/': 'Группы',
        }
    }


def is_student(user):
    return user.groups.filter(name='Student').exists()


def is_teacher(user):
    return user.groups.filter(name='Teacher').exists()


def index(request):
    context = get_base_context('Главная')
    tasks = Task.objects.filter(visible=True).values()

    if request.user.is_authenticated and is_student(request.user):
        student = Student.objects.get(user=request.user)
        for task in tasks:
            work = Work.objects.filter(student=student, task_id=task['id']).values()
            if work.exists():
                work = work[0]
                task['variant'] = work['variant']

    context['tasks'] = tasks
    return render(request, 'index.html', context)
