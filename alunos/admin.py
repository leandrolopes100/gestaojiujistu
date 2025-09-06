from django.contrib import admin
from django.utils.html import format_html
from datetime import date, timedelta
from alunos.models import Aluno, GeneroAluno, MetodoPagamentoAluno, PagamentoAluno, GraduacaoAluno, TipoTurmaAluno, Produto, Despesa, DespesaMensal

from django.contrib import admin
from django.utils.html import format_html
from datetime import date, timedelta
from .models import Aluno

# Registro do Aluno
@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'pagamento_aluno', 'data_pagamento', 'proximo_pagamento_colorido')

    def proximo_pagamento_colorido(self, obj):
        if not obj.proximo_pagamento:
            return format_html('<span style="color: gray;">--</span>')

        hoje = date.today()
        if obj.proximo_pagamento < hoje:
            cor = 'red'
            status = 'Atrasado'
        elif obj.proximo_pagamento <= hoje + timedelta(days=5):
            cor = 'orange'
            status = 'Vencendo'
        else:
            cor = 'green'
            status = 'Em dia'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ({})</span>',
            cor,
            obj.proximo_pagamento.strftime('%d/%m/%Y'),
            status
        )

    proximo_pagamento_colorido.short_description = 'Próx. Pagamento'

# Registro dos outros models
@admin.register(GeneroAluno)
class GeneroAlunoAdmin(admin.ModelAdmin):
    list_display = ['genero']
    search_fields = ['genero']

@admin.register(MetodoPagamentoAluno)
class MetodoPagamentoAlunoAdmin(admin.ModelAdmin):
    list_display = ['metodo']
    search_fields = ['metodo']

@admin.register(PagamentoAluno)
class PagamentoAlunoAdmin(admin.ModelAdmin):
    list_display = ['pagamento']
    search_fields = ['pagamento']

@admin.register(GraduacaoAluno)
class GraduacaoAlunoAdmin(admin.ModelAdmin):
    list_display = ['faixa']
    search_fields = ['faixa']

@admin.register(TipoTurmaAluno)
class TipoTurmaAlunoAdmin(admin.ModelAdmin):
    list_display = ['categoria_etaria']
    search_fields = ['categoria_etaria']

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome_produto', 'valor_produto', 'data_venda', 'quantidade', 'valor_total', 'metodo_pagamento']

@admin.register(DespesaMensal)
class DespesaMensalAdmin(admin.ModelAdmin):
    list_display = ['nome_despesa']

@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'valor_despesa', 'data_despesa']

