from django.urls import path
from django.contrib.auth import views as auth_views
import ClassManager.views.main as views
import ClassManager.views.student as student
import ClassManager.views.teacher as teacher

urlpatterns = [
    path('', views.index),
    path('login/', auth_views.LoginView.as_view(extra_context=views.get_base_context('Вход')), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('student/profile/', student.profile),
    path('student/works/', student.works),

    path('teacher/tasks/', teacher.tasks),
    path('teacher/checking/', teacher.checking),
    path('teacher/students/', teacher.students),
    path('teacher/groups/', teacher.groups),
]
