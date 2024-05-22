from .models import *
from datetime import date
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from pytz import timezone as pytz_timezone 
from book.models import Livro , Emprestimo
from django.db import IntegrityError, transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from book.forms import BookRegister ,FiltroLivroForm, CategoryRegister


def index(request):
        # livros_sem_usuario = Livro.objects.filter(usuario__isnull=True)
        forms_livro = BookRegister()
        forms_categoria = CategoryRegister()
        form_filtro = FiltroLivroForm(request.GET)
        livros = Livro.objects.all()
        categorias = Livro.objects.values_list('categoria', flat=True).distinct()

        if form_filtro.is_valid():
            categoria = form_filtro.cleaned_data.get('categoria')
            emprestado = form_filtro.cleaned_data.get('emprestado')
            nome_livro = form_filtro.cleaned_data.get('nome_livro')

            if categoria:
                livros = livros.filter(categoria=categoria)
            
            if emprestado:
                if emprestado == 'emprestado':
                    livros = livros.filter(emprestado=True)
                elif emprestado == 'disponivel':
                    livros = livros.filter(emprestado=False)
        if nome_livro:  # Novo bloco para filtrar por nome do livro
            livros = livros.filter(nome__icontains=nome_livro)

        if request.user.is_authenticated:
            messages.success(request, "Você foi logado com sucesso!")
        else:
            aviso = "Aviso importante: Esta página não exige Login"
            messages.warning(request, aviso)
        return render(request, "index.html", {'titulo': 'Ultimos Livros','livros':livros,'form_livro': forms_livro,'form_categoria': forms_categoria,"form_filtro":form_filtro,'categorias': categorias}) #'livros_sem_usuario': livros_sem_usuario


@login_required
def home (request):
    mensagem = " Você foi Logado com Sucesso!!!"
    messages.success(request,mensagem)

    livros = Livro.objects.filter(usuario= request.user)
    emprestimos = Emprestimo.objects.filter(nome_emprestimo = request.user)
    form = BookRegister()
    
    paginator = Paginator(emprestimos, 8)  # 8 empréstimos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context={
        "livros": livros,
        "emprestimos": emprestimos,
        "page_obj": page_obj,
        'form': form,
        'today': date.today()
    }

    return render(request, "library/home.html", context)

def view_book(request,id):
        if request.user.is_authenticated:
            livros = get_object_or_404(Livro,id=id)
            if request.user == livros.usuario or not livros.emprestado:
                # Calcula o tempo restante para devolução do livro se estiver emprestado
                tempo_restante = None
                if livros.emprestado:
                    emprestimo = Emprestimo.objects.filter(livro=livros, nome_emprestimo=request.user, data_devolucao__isnull=True).first()
                    if emprestimo:
                        tempo_restante = emprestimo.data_devolucao - timezone.now()
                        horas = tempo_restante.seconds // 3600
                        minutos = (tempo_restante.seconds // 60) % 60
                        segundos = tempo_restante.seconds % 60
                        tempo_restante = {
                        "dias": tempo_restante.days,
                        "horas": horas,
                        "minutos": minutos,
                        "segundos": segundos
                        }

                context = {
                    "livro": livros,
                    "tempo_restante": tempo_restante
                }
                return render(request, "library/view_book.html", context)
            # if not livros.emprestado:
            #     return render(request, "library/view_book.html", context)
            else:
                return HttpResponse("Esse livro não existe ou não é seu.")
        return redirect('index')



@login_required
def ver_form_emprestimo(request,id):
    livro = get_object_or_404(Livro, id=id)
    return render(request, 'library/loan.html', {'livro': livro})


@login_required
def processar_emprestimo(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        data_devolucao = request.POST.get('data_devolucao')

        # Convertendo a data de devolução para um objeto datetime
        data_devolucao = timezone.datetime.strptime(data_devolucao, '%Y-%m-%d')

        livro = get_object_or_404(Livro, id=livro_id)

        if not livro.emprestado:
            livro.usuario = request.user
            livro.emprestado = True
            livro.save()

            # Obtém o fuso horário de São Paulo, Brasil
            sao_paulo_tz = pytz_timezone('America/Sao_Paulo')
            # Converte a data de devolução para o fuso horário de São Paulo
            data_devolucao = sao_paulo_tz.localize(data_devolucao)
            
            Emprestimo.objects.create(
                nome_emprestimo=request.user,
                data_emprestimo=timezone.now(),
                data_devolucao=data_devolucao,
                livro=livro
            )
            
            messages.success(request, f'O livro "{livro.nome}" foi pego por emprestimo até {data_devolucao.strftime("%d/%m/%Y")}.')
        else:
            messages.error(request, f'O livro "{livro.nome}" já está emprestado.')
    else:
        messages.error(request, 'Ocorreu um erro ao processar o formulário de empréstimo.')

    return redirect('index')

@login_required
def devolver_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    
        # Verificar se o livro está emprestado pelo usuário atual e se pode ser devolvido
    if livro.emprestado and livro.usuario == request.user:
            livro.emprestado = False
            livro.usuario = None
            livro.save()
            messages.success(request, f'Você devolveu o livro "{livro.nome}" com sucesso.')
    else:
            messages.error(request, f'Você não pode devolver o livro "{livro.nome}".')
        
    return redirect('index')  # Redireciona para a página principal



@login_required
def historico_emprestimos(request):
    historico = Emprestimo.objects.filter(usuario=request.user)
    return render(request, 'library/view_book.html', {'historico': historico})

@login_required
def excluir_emprestimo(request, id):
    emprestimo = get_object_or_404(Emprestimo, id=id)
    emprestimo.delete()
    messages.success(request, 'Empréstimo excluído com sucesso.')
    return redirect('home')

@login_required
def cadastrar_livro(request):
    if request.method == 'POST':
        form_livro = BookRegister(request.POST,request.FILES)

        if form_livro.is_valid:
            form_livro.save()
            messages.success(request, 'Livro Cadastrado com Sucesso')
        else:
            messages.warning(request, 'Cadastro do Livro falhou')
            return redirect('index')
    return redirect('index')

@login_required
def excluir_livro(request, id):
    livro = get_object_or_404(Livro, id=id)
    
    # Verificar se há algum empréstimo associado a este livro
    emprestimos_associados = Emprestimo.objects.filter(livro=livro)
    if emprestimos_associados.exists():
        messages.error(request, 'Este livro não pode ser excluído porque ainda está emprestado.')
        return redirect('index')

    try:
        with transaction.atomic():
            livro.delete()
        messages.success(request, 'Livro excluído com sucesso.')
    except IntegrityError:
        messages.error(request, 'Erro ao excluir o livro devido a uma falha de integridade de chave estrangeira.')
    
    return redirect('index')

@login_required
def cadastrar_categoria(request):
    if request.method == 'POST':
        form_categoria = CategoryRegister(request.POST)

        if form_categoria.is_valid():
            form_categoria.save()
            messages.success(request, 'Categoria Cadastrado com Sucesso')
        else:
            messages.warning(request, 'Cadastro da Categoria falhou')
            return redirect('index')
    return redirect('index')