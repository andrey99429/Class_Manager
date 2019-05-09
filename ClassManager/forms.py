from django import forms

attrs = {'class': 'form-control', 'autocomplete': 'off'}


class StudentMail_Form(forms.Form):
    gmail = forms.EmailField(widget=forms.EmailInput(attrs=attrs))


class Task_Form(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(label='Название', max_length=100, widget=forms.TextInput(attrs=attrs))
    description = forms.CharField(label='Описание', max_length=500, widget=forms.Textarea(attrs=attrs))
    deadline = forms.DateTimeField(label='Срок сдачи', widget=forms.DateTimeInput(attrs=attrs))
    variants = forms.IntegerField(label='Кол-во вариантов', min_value=1, widget=forms.NumberInput(attrs=attrs))
    file_name = forms.CharField(label='Название файла', max_length=50, widget=forms.TextInput(attrs=attrs))
    visible = forms.BooleanField(label='Опубликовано', required=False, widget=forms.CheckboxInput(attrs=attrs))


class Student_Form(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    group = forms.CharField(label='Группа', widget=forms.TextInput(attrs=attrs))
    name = forms.CharField(label='Имя', max_length=50, widget=forms.TextInput(attrs=attrs))
    surname = forms.CharField(label='Фамилия', max_length=50, widget=forms.TextInput(attrs=attrs))
    patronymic = forms.CharField(label='Отчество', max_length=50, widget=forms.TextInput(attrs=attrs))
    gmail = forms.EmailField(label='gmail', required=False, max_length=100, widget=forms.EmailInput(attrs=attrs))


class Group_Form(forms.Form):
    id = forms.IntegerField(widget=forms.HiddenInput())
    name = forms.CharField(label='Название', max_length=6, widget=forms.TextInput(attrs=attrs))


class Mark_Form(forms.Form):
    work_id = forms.IntegerField(widget=forms.HiddenInput())
    mark = forms.FloatField()
    comment = forms.CharField(label='Комментарий:', required=False)
