from django import forms 
from .models import Livro, Categoria


class BookRegister(forms.ModelForm):

    class Meta:
        model = Livro
        fields = ('image','nome','autor','sinopse','editora','categoria',)

class CategoryRegister(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ('nome',)

class FiltroLivroForm(forms.Form):
    CATEGORIAS_CHOICES = (
        ('', 'Todas as categorias'),  # Opção vazia para selecionar todas as categorias
        # Adicione suas opções de categoria aqui, se necessário
    )

    EMPRESTADO_CHOICES = (
        ('', 'Todos'),  # Opção vazia para mostrar todos os livros, independentemente do status de empréstimo
        ('emprestado', 'Emprestados'),
        ('disponivel', 'Disponíveis'),
    )

    categoria = forms.ChoiceField(choices=CATEGORIAS_CHOICES, required=False)
    emprestado = forms.ChoiceField(choices=EMPRESTADO_CHOICES, required=False)
    nome_livro = forms.CharField(label='Nome do Livro', required=False)