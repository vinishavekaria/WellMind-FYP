from django.urls import path
from accounts import views
from .views import mood_pixel_chart_view
#from .views import ai_chatbot
from django.views.generic import TemplateView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('welcome/', views.welcome_page, name='welcome'),
    path('journal/', views.journal_entry_view, name='journal_entry'), 
    path('entries/', views.journal_entries_view, name='journal_entries'), 
    path('update-journal/<int:entry_id>/', views.update_journal_entry, name='update_journal'),
    path('delete-journal/<int:entry_id>/', views.delete_journal_entry, name='delete_journal'),
    path('mood-dashboard/', views.mood_dashboard_view, name='mood_dashboard'),
    path('mood-chart/', mood_pixel_chart_view, name='mood_chart'),
    path('sentiment_line_chart/', views.sentiment_line_chart_view, name='sentiment_line_chart'),
    path('mood-pie-chart/', views.mood_pie_chart_view, name='mood_pie_chart'),
    path('todo/', views.todo_list, name='todo_list'),
    path('todo/delete/<int:pk>/', views.delete_todo, name='delete_todo'),
    path('todo/amend/<int:pk>/', views.amend_todo, name='amend_todo'),
    path('wellness-tips/', views.wellness_tips_view, name='wellness_tips'),
    path('mood_music/', views.mood_music, name='mood_music'),
    path('save_favorite/', views.save_favorite, name='save_favorite'),
    path('resources/', views.resources_view, name='resources'),
    #path('ai_chatbot/', ai_chatbot, name='ai_chatbot'),

]
