# from django import template
# from datetime import datetime

# register = template.Library()

# @register.filter
# def mostra_duracao(value1, value2):
#     if isinstance(value1, datetime) and isinstance(value2, datetime):
#         diferenca = value1 - value2
        
#         # Verifica se a diferença é negativa ou zero
#         if diferenca.total_seconds() <= 0:
#             # Se o prazo já expirou, retorna "Expirado" em vermelho
#             return '<span style="color: red;">Expirado</span>'
#         else:
#             # Calcula dias, horas e minutos restantes
#             dias = diferenca.days
#             horas, segundos = divmod(diferenca.seconds, 3600)
#             minutos = segundos // 60
            
#             # Formata a string de tempo restante
#             tempo_restante = ""
#             if dias > 0:
#                 tempo_restante += f"{dias} dias "
#             if horas > 0:
#                 tempo_restante += f"{horas} horas "
#             if minutos > 0:
#                 tempo_restante += f"{minutos} minutos"
            
#             return tempo_restante
    
#     # Se os valores não forem datetime, retorna uma string vazia
#     return ""
from django import template
from datetime import datetime

register = template.Library()

@register.filter
def mostra_duracao(value1, value2):
    """
    Calcula a diferença entre duas datas e retorna uma string formatada.
    
    Args:
    value1 (datetime): Primeira data (futura).
    value2 (datetime): Segunda data (passada).
    
    Returns:
    str: Tempo restante ou "Expirado" em vermelho se o prazo já tiver passado.
    """
    if isinstance(value1, datetime) and isinstance(value2, datetime):
        diferenca = value1 - value2
        
        if diferenca.total_seconds() <= 0:
            return '<span class="expirado">Expirado</span>'
        else:
            return f'<span class="duracao" data-end="{value1.isoformat()}" data-start="{value2.isoformat()}"></span>'
    
    return ""

