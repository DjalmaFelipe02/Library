from django.urls import path 
from . import views

urlpatterns = [
    path('',views.index, name='index'),
    path('home/',views.home, name='home'),
    path('view_book/<int:id>', views.view_book, name='view_book'),
    path('devolver_livro/<int:id>/', views.devolver_livro, name='devolver_livro'),
    path('processar_emprestimo/', views.processar_emprestimo, name="processar_emprestimo"),
    path('ver_form_emprestimo/<int:id>/', views.ver_form_emprestimo, name='ver_form_emprestimo'),
    path('historico-emprestimos/', views.historico_emprestimos, name='historico_emprestimos'),
    path('excluir_emprestimo/<int:emprestimo_id>/', views.excluir_emprestimo, name='excluir_emprestimo'),
    path('cadastrar_livro/', views.cadastrar_livro, name='cadastrar_livro'),
    path('excluir_livro/<int:id>/', views.excluir_livro, name='excluir_livro'),
    path('cadastrar_categoria/', views.cadastrar_categoria, name='cadastrar_categoria'),

]