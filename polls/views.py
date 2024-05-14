from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *

def index(request):
    aviso = "Aviso importante: Esta página não exige Login"
    messages.warning(request, aviso)
    return render(request, "index.html", {'titulo': 'Ultimas enquetes'})


@login_required
def ola (request):
    questions  = Question.objects.all()
    mensagem = " Você foi Logado com Sucesso!!!"
    messages.success(request,mensagem)
    
    context={
        "all_questions": questions
    }

    return render(request, "polls/questions.html", context)
    
