from .models import *
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Avg
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from book.models import Livro,Emprestimo,Categoria, Avaliacao
from book.forms import BookRegister ,FiltroLivroForm, CategoryRegister, AvaliacaoForm


def index(request):
        # livros_sem_usuario = Livro.objects.filter(usuario__isnull=True)
        forms_livro = BookRegister()
        forms_categoria = CategoryRegister()
        form_filtro = FiltroLivroForm(request.GET)
        livros = Livro.objects.all()
        categorias = Categoria.objects.all()

        # Inicialize as variáveis de filtragem
        categoria_id = None
        emprestado = None
        nome_livro = None

        if form_filtro.is_valid():
            categoria_id = form_filtro.cleaned_data.get('categoria')
            emprestado = form_filtro.cleaned_data.get('emprestado')
            nome_livro = form_filtro.cleaned_data.get('nome_livro')

            if categoria_id:
                livros = livros.filter(categoria_id=categoria_id)
            
            if emprestado:
                if emprestado == 'emprestado':
                    livros = livros.filter(emprestado=True)
                elif emprestado == 'disponivel':
                    livros = livros.filter(emprestado=False)
        if nome_livro:  # Novo bloco para filtrar por nome do livro
            livros = livros.filter(nome__icontains=nome_livro)

        for livro in livros:
            media_avaliacoes = Avaliacao.objects.filter(livro=livro).aggregate(media=Avg('nota'))['media']
            livro.media_avaliacoes = media_avaliacoes

        paginator = Paginator(livros, 12)  # 10 livros por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        if request.user.is_authenticated:
            messages.success(request, "Você foi logado com sucesso!")
        else:
            aviso = "Aviso importante: Esta página não exige Login"
            messages.warning(request, aviso)
        return render(request, "index.html", {'titulo': 'Ultimos Livros','livros':livros,'form_livro': forms_livro,'form_categoria': forms_categoria,
                                              "form_filtro":form_filtro,'categorias': categorias,'page_obj': page_obj,})

@login_required
def home(request):
    mensagem = "Você foi logado com sucesso!"
    messages.success(request, mensagem)

    # Obter os livros do usuário
    livros = Livro.objects.filter(usuario=request.user)
    form = BookRegister()

    # Obter os empréstimos do usuário
    emprestimos = Emprestimo.objects.filter(nome_emprestimo=request.user).order_by('-data_emprestimo')


    # Paginação dos empréstimos
    paginator = Paginator(emprestimos, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for emprestimo in emprestimos:
        if emprestimo.data_devolucao > timezone.now():
            tempo_restante = emprestimo.data_devolucao - timezone.now()
            dias = tempo_restante.days
            horas, minutos = divmod(tempo_restante.seconds, 3600)
            minutos, segundos = divmod(minutos, 60)
            emprestimo.tempo_restante = {
                "dias": dias,
                "horas": horas,
                "minutos": minutos,
                "segundos": segundos
            }
        else:
            emprestimo.expirado = True

    # Calcular a média de avaliações para cada livro do usuário
    livros_com_avaliacoes = []
    for livro in livros:
        media_avaliacoes = Avaliacao.objects.filter(livro=livro).aggregate(media=Avg('nota'))['media']
        livros_com_avaliacoes.append({
            'livro': livro,
            'media_avaliacoes': media_avaliacoes,
        })

    context = {
        "livros_com_avaliacoes": livros_com_avaliacoes,
        "livros": livros,
        "emprestimos": emprestimos,
        "tempo_restante": tempo_restante,
        "page_obj": page_obj,
        'form': form,
        'today': timezone.now(),
    }

    return render(request, "library/home.html", context)

def view_book(request, id):
    livro = get_object_or_404(Livro, id=id)
    tempo_restante = None
    pode_avaliar = False

    if request.user.is_authenticated:
        emprestimo = Emprestimo.objects.filter(livro=livro, nome_emprestimo=request.user, data_devolucao__gt=timezone.now()).first()
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
            pode_avaliar = True

    avaliacoes = Avaliacao.objects.filter(livro=livro)
    media_avaliacoes = avaliacoes.aggregate(media=Avg('nota'))['media']

    context = {
        "livro": livro,
        "tempo_restante": tempo_restante,
        "pode_avaliar": pode_avaliar,
        "media_avaliacoes": media_avaliacoes
    }
    return render(request, "library/view_book.html", context)



@login_required
def ver_form_emprestimo(request,id):
    livro = get_object_or_404(Livro, id=id)
    return render(request, 'library/loan.html', {'livro': livro})

########EMPRÉSTIMOS#################EMPRÉSTIMOS########################EMPRÉSTIMOS################################################################################################################################
@login_required
def processar_emprestimo(request):
    if request.method == 'POST':
        livro_id = request.POST.get('livro_id')
        quantidade_dias = request.POST.get('quantidade_dias')

        try:
            quantidade_dias = int(quantidade_dias)
        except ValueError:
            messages.error(request, 'A quantidade de dias informada não é válida.')
            return redirect('index')

        if quantidade_dias < 1 or quantidade_dias > 14:
            messages.error(request, 'A quantidade de dias deve estar entre 1 e 14.')
            return redirect('index')

        livro = get_object_or_404(Livro, id=livro_id)

        if not livro.emprestado:
            livro.usuario = request.user
            livro.emprestado = True
            livro.save()

            # Calcula a data de devolução baseada na quantidade de dias
            data_devolucao = timezone.now() + timedelta(days=quantidade_dias)

            # Verifica se o livro já foi emprestado antes
            emprestimo_anterior = Emprestimo.objects.filter(livro=livro, data_devolucao__isnull=True).first()

            if emprestimo_anterior:
                # Se o livro já foi emprestado antes, atualize o período de empréstimo
                emprestimo_anterior.data_devolucao = data_devolucao
                emprestimo_anterior.save()

            Emprestimo.objects.create(
                nome_emprestimo=request.user,
                data_emprestimo=timezone.now(),
                data_devolucao=data_devolucao,
                livro=livro
            )

            messages.success(request, f'O livro "{livro.nome}" foi pego emprestado por {quantidade_dias} dias.')
        else:
            messages.error(request, f'O livro "{livro.nome}" já está emprestado.')
    else:
        messages.error(request, 'Método inválido para processar o formulário de empréstimo.')

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


##############CADASTRO E EXCLUSÃO DE LIVROS###################################################################################################################################################################

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
    livro = Livro.objects.get(id=id)
    livro.delete()
    messages.success(request, 'Livro excluído com sucesso.')

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

############### AVALIAÇÃO  ####################################################################################################################################################################

@login_required
def avaliar_livro(request, id):
    livro = get_object_or_404(Livro, id=id)

    # Verificar se o usuário está com o livro emprestado
    emprestimo = Emprestimo.objects.filter(livro=livro, nome_emprestimo=request.user, data_devolucao__gt=timezone.now()).first()

    if emprestimo:
        if request.method == 'POST':
            form = AvaliacaoForm(request.POST)
            if form.is_valid():
                avaliacao = form.save(commit=False)
                avaliacao.livro = livro
                avaliacao.usuario = request.user
                avaliacao.save()
                messages.success(request, 'Avaliação salva com sucesso.')
                return redirect('view_book', id=livro.id)
        else:
            form = AvaliacaoForm()
        return render(request, 'library/avaliation/rate.html', {'form': form, 'livro': livro})
    else:
        messages.error(request, 'Você não pode avaliar este livro porque não está com ele emprestado.')
        return redirect('detalhe_livro', id=livro.id)

@login_required
def ver_avaliacoes(request, id):
    livro = get_object_or_404(Livro, id=id)
    avaliacoes = Avaliacao.objects.filter(livro=livro)
    total_avaliacoes = avaliacoes.count()

    total_avaliacoes = avaliacoes.count()
    distribuicao_notas = {
        1: avaliacoes.filter(nota=1).count(),
        2: avaliacoes.filter(nota=2).count(),
        3: avaliacoes.filter(nota=3).count(),
        4: avaliacoes.filter(nota=4).count(),
        5: avaliacoes.filter(nota=5).count(),
    }

    percentuais = {nota: (contagem / total_avaliacoes) * 100 if total_avaliacoes > 0 else 0 for nota, contagem in distribuicao_notas.items()}

    context = {
        "livro": livro,
        "avaliacoes": avaliacoes,
        "percentuais": percentuais,
        'total_avaliacoes': total_avaliacoes,
    }

    return render(request, 'library/avaliation/view_avaliation.html', context)