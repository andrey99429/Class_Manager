from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from ClassManager.views.main import get_base_context, is_student
from ClassManager.models import Student, Work
from ClassManager.forms import StudentMail_Form
from ClassManager.common import edit_student_folder, folder_link, file_link


@login_required
@user_passes_test(is_student)
def profile(request):
    context = get_base_context('Профиль')

    student = Student.objects.get(user=request.user)

    form = StudentMail_Form()
    if request.method == 'POST':
        form = StudentMail_Form(request.POST)
        if form.is_valid():
            edit_student_folder(student, form.cleaned_data['gmail'], student.surname)
            student.save()

    context['data'] = {
        'Имя': student.name,
        'Фамилия': student.surname,
        'Отчество': student.patronymic,
        'Группа': student.group.name,
        'gmail': student.gmail if student.gmail is not None else 'Не указан',
        'Папка с работами': folder_link(student.folder_id) if student.folder_id is not None else 'Для создания необходимо ввести gmail.',
    }
    form.initial['gmail'] = student.gmail if student.gmail is not None else ''
    context['form'] = form
    return render(request, 'student/profile.html', context)


@login_required
@user_passes_test(is_student)
def works(request):
    context = get_base_context('Работы')

    student = Student.objects.get(user=request.user)
    works = Work.objects.filter(student=student).values('task__name', 'task__deadline', 'file_id', 'modified_time', 'variant', 'mark', 'comment')

    for work in works:
        work['file_link'] = file_link(work['file_id']) if work['file_id'] is not None else ''
        work['mark'] = work['mark'] if work['mark'] is not None else ''
        work['comment'] = work['comment'].replace('\r\n', '<br>') if work['comment'] is not None else ''
        print(work['comment'])

    context['works'] = works

    return render(request, 'student/works.html', context)
