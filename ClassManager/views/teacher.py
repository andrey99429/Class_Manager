from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group as UserGroup
from django.contrib.auth.decorators import login_required, user_passes_test
from ClassManager.views.main import get_base_context, is_teacher
from ClassManager.models import Student, Work, Task, Group
from ClassManager.forms import Task_Form, Student_Form, Group_Form, Mark_Form
from GoogleAPI.manager import local_now
from ClassManager.common import edit_student_folder, folder_link, file_view, generate_password, criteria, mark_round


@login_required
@user_passes_test(is_teacher)
def tasks(request):
    context = get_base_context('Задания')
    context['heading'] = 'Редактирование задания'

    if request.method == 'POST':
        form = Task_Form(request.POST)
        if form.is_valid():
            task = Task.objects.get(id=form.cleaned_data['id'])
            task.name = form.cleaned_data['name']
            task.description = form.cleaned_data['description']
            task.deadline = form.cleaned_data['deadline']
            task.variants = form.cleaned_data['variants']
            task.file_name = form.cleaned_data['file_name']
            task.visible = form.cleaned_data['visible']
            task.save()
            return redirect('/teacher/tasks/')
        else:
            context['form'] = form
            return render(request, 'teacher/editing.html', context)
    else:
        if 'id' in request.GET:
            if request.GET['id'] == '-1':
                task = Task(name='Название', description='Описание', deadline=local_now(), file_name='name.pdf', variants=30, visible=False)
                task.save()
                return redirect('/teacher/tasks/?id='+str(task.id))
            else:
                task = Task.objects.filter(id=request.GET['id'])
                if not task.exists():
                    return redirect('/teacher/tasks/')
                task = task[0]

            form = Task_Form()

            form.initial['id'] = task.id
            form.initial['name'] = task.name
            form.initial['description'] = task.description
            form.initial['deadline'] = task.deadline
            form.initial['variants'] = task.variants
            form.initial['file_name'] = task.file_name
            form.initial['visible'] = task.visible

            context['form'] = form
            return render(request, 'teacher/editing.html', context)
        else:
            tasks = Task.objects.all().values()
            for task in tasks:
                task['done'] = Work.objects.filter(task_id=task['id'], file_id__isnull=False).count()
                task['marked'] = Work.objects.filter(task_id=task['id'], mark__isnull=False).count()
            context['tasks'] = tasks
            return render(request, 'teacher/tasks.html', context)


@login_required
@user_passes_test(is_teacher)
def students(request):
    context = get_base_context('Студенты')
    context['heading'] = 'Редактирование студента'

    if request.method == 'POST':
        form = Student_Form(request.POST)
        if form.is_valid():
            student = Student.objects.get(id=form.cleaned_data['id'])
            edit_student_folder(student, form.cleaned_data['gmail'], form.cleaned_data['surname'])
            student.name = form.cleaned_data['name']
            student.surname = form.cleaned_data['surname']
            if student.user_id is not None:
                student.user.first_name = student.name
                student.user.last_name = student.surname
                student.user.save()
            student.patronymic = form.cleaned_data['patronymic']
            student.gmail = form.cleaned_data['gmail']
            group = Group.objects.filter(name=form.cleaned_data['group'])
            if group.exists():
                student.group = group[0]
            student.save()
            return redirect('/teacher/students/')
        else:
            context['form'] = form
            return render(request, 'teacher/editing.html', context)
    else:
        if 'id' in request.GET:
            if request.GET['id'] == '-1':
                student = Student(name='Имя', surname='Фамилия', patronymic='Отчество', group=Group.objects.first())
                student.save()
                return redirect('/teacher/students/?id=' + str(student.id))
            else:
                student = Student.objects.filter(id=request.GET['id'])
                if not student.exists():
                    return redirect('/teacher/students/')
                student = student[0]

            form = Student_Form()

            form.initial['id'] = student.id
            form.initial['name'] = student.name
            form.initial['surname'] = student.surname
            form.initial['patronymic'] = student.patronymic
            form.initial['group'] = student.group.name
            form.initial['gmail'] = student.gmail

            context['form'] = form
            return render(request, 'teacher/editing.html', context)
        elif 'create_users' in request.GET:
            students = Student.objects.filter(user_id__isnull=True)
            users = []
            for student in students:
                login = 'stud{}'.format(student.id)
                password = generate_password()

                user = User.objects.create_user(username=login, password=password)
                user.groups.add(UserGroup.objects.get(name='Student'))
                user.first_name = student.name
                user.last_name = student.surname
                user.save()

                student.user_id = user.id
                student.save()

                users.append({
                    'group': student.group.name,
                    'fullname': '{} {} {}'.format(student.surname, student.name, student.patronymic),
                    'login': login,
                    'password': password
                })

            context['users'] = users
            return render(request, 'teacher/students.html', context)
        else:
            students = Student.objects.all().order_by('group__name', 'surname', 'name', 'patronymic').values()
            for student in students:
                student['group'] = Group.objects.get(id=student['group_id']).name
                student['folder_link'] = folder_link(student['folder_id']) if student['folder_id'] is not None else 'Не создана'
                student['gmail'] = student['gmail'] if student['gmail'] is not None else 'Не указан'
                student['user_id'] = student['user_id'] if student['user_id'] is not None else 'Не создан'

            context['students'] = students
            return render(request, 'teacher/students.html', context)


@login_required
@user_passes_test(is_teacher)
def groups(request):
    context = get_base_context('Группы')
    context['heading'] = 'Редактирование группы'

    if request.method == 'POST':
        form = Group_Form(request.POST)
        if form.is_valid():
            group = Group.objects.get(id=form.cleaned_data['id'])
            group.name = form.cleaned_data['name']
            group.save()
            return redirect('/teacher/groups/')
        else:
            context['form'] = form
            return render(request, 'teacher/editing.html', context)
    else:
        if 'id' in request.GET:
            if request.GET['id'] == '-1':
                group = Group(name='Название')
                group.save()
                return redirect('/teacher/groups/?id='+str(group.id))
            else:
                group = Group.objects.filter(id=request.GET['id'])
                if not group.exists():
                    return redirect('/teacher/groups/')
                group = group[0]

            form = Group_Form()

            form.initial['id'] = group.id
            form.initial['name'] = group.name

            context['form'] = form
            return render(request, 'teacher/editing.html', context)
        else:
            groups = Group.objects.all().values()
            for group in groups:
                group['stud_count'] = Group.objects.get(id=group['id']).student_set.count()
            context['groups'] = groups
            return render(request, 'teacher/groups.html', context)


@login_required
@user_passes_test(is_teacher)
def checking(request):
    context = get_base_context('Проверка работ')
    if request.method == 'POST':
        form = Mark_Form(request.POST)
        if form.is_valid():
            work = Work.objects.get(id=form.cleaned_data['work_id'])
            work.mark = mark_round(form.cleaned_data['mark'])
            work.comment = form.cleaned_data['comment']
            work.save()
            return redirect('/teacher/checking/?work_id={}'.format(work.id))
        else:
            return redirect('/teacher/tasks/')
    else:
        task = None
        if 'work_id' in request.GET:
            work = Work.objects.filter(id=request.GET['work_id']).values()
            if not work.exists():
                return redirect('/teacher/tasks/')
            work = work[0]
            task = Task.objects.get(id=work['task_id'])
            work['link'] = file_view(work['file_id']) if work['file_id'] is not None else None
            work['mark'] = work['mark'] if work['mark'] is not None else ''
            work['modified_time'] = work['modified_time'] if work['modified_time'] is not None else 'Не загружено'
            work['comment'] = work['comment'] if work['comment'] is not None else ''

            form = Mark_Form()
            form.initial['work_id'] = work['id']
            form.initial['mark'] = work['mark']
            form.initial['comment'] = work['comment']

            context['form'] = form
            context['criteria'] = criteria
            context['work'] = work
            context['student'] = Student.objects.filter(id=work['student_id']).values()[0]
            context['student']['group'] = Group.objects.filter(id=context['student']['group_id']).values()[0]['name']
            context['current_work'] = work['id']

        elif 'task_id' in request.GET:
            task = Task.objects.filter(id=request.GET['task_id'])
            if not task.exists():
                return redirect('/teacher/tasks/')
            task = task[0]

        works = Work.objects.filter(task=task)
        works_list = {}
        for work in works:
            if work.variant not in works_list:
                works_list[work.variant] = []
            works_list[work.variant].append({
                'id': work.id,
                'stud_fullname': '{} {}'.format(work.student.surname, work.student.name),
                'mark': work.mark if work.mark is not None else '',
            })
        works_list = list(works_list.items())
        works_list.sort()
        context['task'] = task
        context['works_list'] = works_list
        return render(request, 'teacher/checking.html', context)
