from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        '',
        auth_views.LoginView.as_view(
            template_name='login.html'
        ),
        name='login'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),
    path('queues/', views.manage_queues, name='manage_queues'),
    path('queues/<int:queue_id>/', views.queue_details, name='queue_details'),
    path(
    'token/<int:token_id>/move-up/', views.move_token,{'direction': 'up'},name='move_token_up'
),

path(
    'token/<int:token_id>/move-down/',
    views.move_token,
    {'direction': 'down'},
    name='move_token_down'
),

path(
    'queues/<int:queue_id>/call-next/',
    views.call_next_token,
    name='call_next_token'
),
path(
    'token/<int:token_id>/complete/',
    views.complete_token,
    name='complete_token'
),
path(
    'token/<int:token_id>/cancel/',
    views.cancel_token,
    name='cancel_token'
),
path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]