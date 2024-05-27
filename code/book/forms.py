from django import forms 
from .models import Livro, Categoria, Avaliacao


class BookRegister(forms.ModelForm):

    class Meta:
        model = Livro
        fields = ('image','nome','autor','sinopse','editora','categoria',)

class CategoryRegister(forms.ModelForm):

    class Meta:
        model = Categoria
        fields = ('nome',)

class FiltroLivroForm(forms.Form):
    nome_livro = forms.CharField(required=False)
    categoria = forms.ModelChoiceField(queryset=Categoria.objects.all(), required=False)  # Certifique-se de que o campo é do tipo ModelChoiceField
    emprestado = forms.ChoiceField(choices=(('', 'Todos'),('emprestado', 'Emprestados'), ('disponivel', 'Disponíveis')), required=False)

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ['nota', 'comentario']
        widgets = {
            'nota': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }