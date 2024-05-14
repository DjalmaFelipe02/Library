from django.db import models

class Question(models.Model):
    question_text = models.CharField("Pergunta" , max_length=200)
    pub_date = models.DateField("Data de Publicação")
