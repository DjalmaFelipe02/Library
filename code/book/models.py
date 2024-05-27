from django.db import models
from account.models import CustomUser

class Categoria(models.Model):
    nome= models.CharField(max_length=20)
    
    def __str__(self):
        return self.nome

class Livro(models.Model):
    image = models.ImageField(upload_to='capa_livros',default="")
    nome = models.CharField(max_length=80)
    autor = models.CharField(max_length=30)
    sinopse = models.TextField(max_length=1200)
    editora = models.CharField(max_length=20)
    data_cadastro = models.DateField(auto_now_add=True)
    emprestado= models.BooleanField(default=False)
    categoria = models.ForeignKey(Categoria, on_delete=models.DO_NOTHING )
    usuario = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING,null=True, blank=True)

    def __str__(self):
        return self.nome

class Emprestimo(models.Model):
    nome_emprestimo =models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    data_emprestimo = models.DateTimeField(blank=True,null=True)
    data_devolucao = models.DateTimeField(blank=True,null=True)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.nome_emprestimo} - {self.livro.nome}"

class Avaliacao(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    nota = models.PositiveSmallIntegerField()
    comentario = models.TextField(max_length=1000)
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.livro} - {self.nota}"
    