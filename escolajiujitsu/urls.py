
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from alunos.views import (
    CustomLoginView,
    CustomLogoutView,
    DashboardView,
    AlunosListView,
    AlunosCreateView,
    AlunosUpdateView,
    AlunoDetailView,
    AlunoDeleteView,
    RelatorioReceberView,
    VendaProduto,
    RegistrarPagamentoView,
    DespesasView,
    DespesasListView,
    DespesasDeleteView,
    DespesasUpdateView,
    exportar_relatorio_recebidos_pdf
  )

from alunos.views import exportar_relatorio_despesas_pdf

urlpatterns = [
    path('admin/', admin.site.urls),

    # ALUNOS ----------------------------------------------------------------------
    path('alunos/', AlunosListView.as_view(), name='lista_alunos'),
    path('alunos/cadastrar/', AlunosCreateView.as_view(), name='cadastrar_aluno'),
    path('alunos/<int:pk>/editar/', AlunosUpdateView.as_view(), name='editar_aluno'),
    path('alunos/<int:pk>/detalhe/', AlunoDetailView.as_view(), name='detalhe_aluno'),
    path('alunos/<int:pk>/excluir/', AlunoDeleteView.as_view(), name='delete_aluno'),

    #FINANCEIRO ------------------------------------------------------------------
    path('financeiro/receber/', RelatorioReceberView.as_view(), name='relatorio_receber'),
    path('financeiro/venda/', VendaProduto.as_view(), name='registrar_venda'),
    path('financeiro/pagamento/', RegistrarPagamentoView.as_view(), name='registrar_pagamento'),
    path('financeiro/despesa/', DespesasView.as_view(), name='registrar_despesa'),
    path('financeiro/despesas/', DespesasListView.as_view(), name='relatorio_despesas'),
    path('financeiro/despesas/excluir/<int:pk>/', DespesasDeleteView.as_view(), name='delete_despesa'),
    path('financeiro/despesas/editar/<int:pk>/', DespesasUpdateView.as_view(), name='update_despesa'),

    #DASHBOARD ------------------------------------------------------------------
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    #LOGIN ----------------------------------------------------------------------
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),

    # EXPORTAR PDF --------------------------------------------------------------------
    path('relatorio_receber/pdf/', exportar_relatorio_recebidos_pdf, name='exportar_relatorio_receber_pdf'),
    path('relatorio_despesa/pdf/', exportar_relatorio_despesas_pdf, name='exportar_relatorio_despesas_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)