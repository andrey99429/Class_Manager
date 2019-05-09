import random
import string
from django.contrib.auth.models import User, Group as UserGroup
from ClassManager.models import Student, Work, Task
from GoogleAPI.manager import DriveManager

password_chars = string.ascii_letters + string.digits


def mark_round(mark):
    if mark % 1 >= 0.5:
        return int(mark) + 1
    else:
        return int(mark)


def generate_password(size=6):
    return ''.join(random.sample(password_chars, size))


def edit_student_folder(student, new_gmail, new_surname):
    dm: DriveManager = DriveManager.get()

    if new_gmail != '' and student.gmail != new_gmail:
        student.gmail = new_gmail
        if student.folder_id is None:
            student.folder_id = dm.create_folder('{}.{}'.format(student.id, student.surname), student.gmail)
        else:
            dm.update_writer(student.folder_id, student.gmail)

    if student.surname != new_surname and student.folder_id is not None:
        student.surname = new_surname
        dm.rename_folder(student.folder_id, '{}.{}'.format(student.id, student.surname))


def folder_link(folder_id):
    return '<a href="https://drive.google.com/drive/u/0/folders/{}" target="_blank">link</a>'.format(folder_id)


def file_link(file_id):
    return '<a href="https://drive.google.com/file/d/{}/view" target="_blank">link</a>'.format(file_id)


def file_view(file_id):
    return 'https://drive.google.com/file/d/{}/preview'.format(file_id)


def find_works():
    print('Find works: started')
    students = Student.objects.filter(folder_id__isnull=False)
    tasks = Task.objects.filter(visible=True)

    for student in students:
        dm: DriveManager = DriveManager.get()
        files = dm.list_files(student.folder_id)

        for task in tasks:
            work = Work.objects.filter(student=student, task=task)
            i = 0
            while i < len(files) and files[i]['name'] != task.file_name:
                i += 1
            if work.exists():
                work = work[0]
            else:
                work = Work(student=student, task=task, variant=student.id % task.variants + 1)
            # work.variant = student.id % task.variants + 1
            if i == len(files):
                work.file_id = None
                work.modified_time = None
            else:
                work.file_id = files[i]['id']
                work.modified_time = files[i]['modifiedTime']
            work.save()
    print('Find works: done')


criteria = [
    ['Модель', [
        ['num', '-0.5 незначительная ошибка в модели'],
        ['num', '-2 значительная ошибка в модели']
    ]],
    ['Лист', [
        ['check', '-1 неправильный размер']
    ]],
    ['Рамка и Штамп', [
        ['num', '-0.5 неправильный стиль', 4],
        ['check', '-0.25 неправильное заполнение штампа']
    ]],
    ['Вид', [
        ['num', '-0.5 неправильный стиль оформления', 4],
        ['check', '-1 неправильная планировка видов'],
        ['num', '-0.25 лишний элемент']
    ]],
    ['Разрез', [
        ['num', '-1 неправильный разрез'],
        ['num', '-0.5 неправильная граница между разрезом и видом'],
        ['num', '-0.5 неправильный стиль обозначения разреза', 4],
        ['num', '-1 лишнее или недостающее обозначение разреза']
    ]],
    ['Штриховка', [
        ['check', '-1 неправильный тип штриховки'],
        ['num', '-0.5 неправильный угол наклона']
    ]],
    ['Текст', [
        ['check', '-0.5 неправильный стиль', 3],
        ['check', '-0.25 неправильная высота']
    ]],
    ['Размеры', [
        ['num', '-0.25 недостающий или лишний размер'],
        ['num', '-0.25 некорректно стоящий размер'],
        ['num', '-0.5 неправильный стиль размеров', 5]
    ]],
    ['Осевые линии', [
        ['num', '-0.25 недостающая или лишная линия'],
        ['num', '-0.25 неправильный отступ от рисунка', 2],
        ['num', '-0.5 неправильный стиль линий', 4]
    ]],
    ['Масштаб', [
        ['check', '-1 некорректный или неуместный масштаб']
    ]],
    ['Другое', [
        ['check', '-0.5 невыполнение особых правил оформления']
    ]]
]


def init_db():
    print('Init db')
    teacher = UserGroup.objects.create(name='Teacher')
    teacher.save()

    student = UserGroup.objects.create(name='Student')
    student.save()

    admin = User.objects.create_user('admin', '', 'admin')
    admin.first_name = 'Админ'
    admin.groups.add(teacher)
    admin.save()