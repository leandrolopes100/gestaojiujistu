import calendar
from datetime import date, datetime
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

from .models import Aluno, Produto  # ajuste conforme seu app
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View
)


from .models import (
    Aluno, GraduacaoAluno, TipoTurmaAluno, MetodoPagamentoAluno,
    Produto, PagamentoAluno, Despesa
)
from .forms import AlunoForm, ProdutoForm, DespesaForm


#---------------------- LOGIN -------------------------
class CustomLoginView(DjangoLoginView):
    template_name = 'login/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        return self.success_url

class CustomLogoutView(DjangoLogoutView):
    next_page = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# ------------------- ALUNOS -------------------

class AlunosListView(LoginRequiredMixin, ListView):
    model = Aluno
    template_name = 'alunos/alunos.html'
    context_object_name = 'alunos'
    paginate_by = 10

    def get_queryset(self):
        qs = Aluno.objects.order_by('-data_cadastro')
        nome = self.request.GET.get('nome')
        cpf = self.request.GET.get('cpf')
        grupo_idade = self.request.GET.get('grupo_idade')
        status_pagamento = self.request.GET.get('status_pagamento')

        if nome:
            qs = qs.filter(nome__icontains=nome)
        if cpf:
            qs = qs.filter(cpf__icontains=cpf)
        if grupo_idade:
            qs = qs.filter(grupo_idade=grupo_idade)
        if status_pagamento:
            qs = [a for a in qs if a.status_pagamento == status_pagamento]  # Lógica depende do método

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get = self.request.GET
        context.update({
            'nome': get.get('nome', ''),
            'cpf': get.get('cpf', ''),
            'grupo_idade_lista': TipoTurmaAluno.objects.all(),
            'grupo_idade_selecionado': get.get('grupo_idade', ''),
            'status_pagamento': get.get('status_pagamento', ''),
            'graduacoes': GraduacaoAluno.objects.all(),
        })
        return context


class AlunosCreateView(LoginRequiredMixin, CreateView):
    model = Aluno
    form_class = AlunoForm
    template_name = 'alunos/alunos_form.html'
    success_url = reverse_lazy('lista_alunos')

    def form_valid(self, form): #Salvar o usuario que cadastrou o aluno
        form.instance.cadastrado_por = self.request.user
        return super().form_valid(form)
    

class AlunosUpdateView(LoginRequiredMixin, UpdateView):
    model = Aluno
    fields = '__all__'
    template_name = 'alunos/alunos_update.html'
    success_url = reverse_lazy('lista_alunos')


class AlunoDetailView(LoginRequiredMixin, DetailView):
    model = Aluno
    template_name = 'alunos/aluno_detail.html'
    context_object_name = 'aluno'


class AlunoDeleteView(LoginRequiredMixin, DeleteView):
    model = Aluno
    template_name = 'alunos/aluno_delete.html'
    success_url = reverse_lazy('lista_alunos')


# ------------------- FINANCEIRO -------------------

class RelatorioReceberView(LoginRequiredMixin, TemplateView):
    template_name = 'financeiro/relatorio_receber.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get = self.request.GET

        data_inicio = parse_date(get.get('data_inicio')) if get.get('data_inicio') else None
        data_fim = parse_date(get.get('data_fim')) if get.get('data_fim') else None
        metodo_pagamento_id = get.get('metodo_pagamento')

        alunos = Aluno.objects.all()
        vendas = Produto.objects.all()

        if data_inicio and data_fim:
            alunos = alunos.filter(data_pagamento__range=(data_inicio, data_fim))
            vendas = vendas.filter(data_venda__range=(data_inicio, data_fim))

        if metodo_pagamento_id:
            alunos = alunos.filter(metodo_pagamento_id=metodo_pagamento_id)
            vendas = vendas.filter(metodo_pagamento_id=metodo_pagamento_id)

        alunos = alunos.order_by('-data_pagamento', '-id')
        vendas = vendas.order_by('-data_venda', '-id')

        vendas_page = Paginator(vendas, 20).get_page(get.get('page'))

        total_pago_alunos = alunos.aggregate(total=Sum('valor_pago'))['total'] or 0
        total_pago_vendas = vendas.aggregate(total=Sum('valor_produto'))['total'] or 0

        context.update({
            'alunos': alunos,
            'vendas': vendas_page,
            'total_pago_alunos': total_pago_alunos,
            'total_pago_vendas': total_pago_vendas,
            'total_geral': total_pago_alunos + total_pago_vendas,
            'data_inicio': get.get('data_inicio'),
            'data_fim': get.get('data_fim'),
            'metodo_pagamento_id': metodo_pagamento_id,
            'metodos_pagamento': MetodoPagamentoAluno.objects.all(),
        })
        return context


class VendaProduto(LoginRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = 'financeiro/registrar_venda.html'
    success_url = reverse_lazy('relatorio_receber')

    def form_valid(self, form):
        if not form.instance.data_venda:
            form.instance.data_venda = now().date()
        return super().form_valid(form)


class RegistrarPagamentoView(LoginRequiredMixin, View):
    template_name = 'financeiro/registrar_pagamento.html'

    def get(self, request):
        return render(request, self.template_name, {
            'alunos': Aluno.objects.order_by('nome'),
            'metodos_pagamento': MetodoPagamentoAluno.objects.all(),
            'hoje': now().date().isoformat(),
        })

    def post(self, request):
        aluno_id = request.POST.get('aluno')
        valor_pago = request.POST.get('valor_pago')
        data_pagamento_str = request.POST.get('data_pagamento')
        metodo_pagamento_id = request.POST.get('metodo_pagamento')

        if not all([aluno_id, valor_pago, data_pagamento_str, metodo_pagamento_id]):
            messages.error(request, "Todos os campos são obrigatórios.")
            return redirect('registrar_pagamento')

        aluno = get_object_or_404(Aluno, id=aluno_id)

        try:
            valor_pago = float(valor_pago)
            if valor_pago <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, "Valor pago inválido.")
            return redirect('registrar_pagamento')

        try:
            data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Data de pagamento inválida.")
            return redirect('registrar_pagamento')

        metodo_pagamento = get_object_or_404(MetodoPagamentoAluno, id=metodo_pagamento_id)

        aluno.valor_pago = valor_pago
        aluno.data_pagamento = data_pagamento
        aluno.metodo_pagamento = metodo_pagamento
        aluno.save()

        messages.success(request, "Pagamento registrado com sucesso!")
        return redirect('relatorio_receber')


# ------------------- DESPESAS -------------------

class DespesasBaseView(LoginRequiredMixin):
    model = Despesa
    success_url = reverse_lazy('relatorio_despesas')


class DespesasView(DespesasBaseView, CreateView):
    form_class = DespesaForm
    template_name = 'financeiro/registrar_despesa.html'


class DespesasDeleteView(DespesasBaseView, DeleteView):
    template_name = 'financeiro/delete_despesa.html'


class DespesasUpdateView(DespesasBaseView, UpdateView):
    fields = '__all__'
    template_name = 'financeiro/update_despesa.html'


class DespesasListView(LoginRequiredMixin, ListView):
    model = Despesa
    template_name = 'financeiro/relatorio_despesa.html'
    context_object_name = 'despesas'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        get = self.request.GET
        if get.get('data_inicio'):
            qs = qs.filter(data_despesa__gte=get['data_inicio'])
        if get.get('data_fim'):
            qs = qs.filter(data_despesa__lte=get['data_fim'])
        return qs.order_by('-data_despesa', 'id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        despesas = context['despesas']
        context.update({
            'total_geral': despesas.aggregate(total=Sum('valor_despesa'))['total'] or 0,
            'data_inicio': self.request.GET.get('data_inicio', ''),
            'data_fim': self.request.GET.get('data_fim', ''),
        })
        return context


# ------------------- DASHBOARD -------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hoje = date.today()
        primeiro_dia = date(hoje.year, hoje.month, 1)
        ultimo_dia = date(hoje.year, hoje.month, calendar.monthrange(hoje.year, hoje.month)[1])

        data_inicio = self.request.GET.get('data_inicio') or primeiro_dia
        data_fim = self.request.GET.get('data_fim') or ultimo_dia

        if isinstance(data_inicio, str):
            data_inicio = date.fromisoformat(data_inicio)
        if isinstance(data_fim, str):
            data_fim = date.fromisoformat(data_fim)

        # Querysets por período (financeiro)
        alunos_periodo = Aluno.objects.filter(data_pagamento__range=[data_inicio, data_fim])
        despesas_qs = Despesa.objects.filter(data_despesa__range=[data_inicio, data_fim])
        vendas_qs = Produto.objects.filter(data_venda__range=[data_inicio, data_fim])

        # Totais financeiros
        total_pago_alunos = alunos_periodo.aggregate(total=Sum('valor_pago'))['total'] or 0
        total_despesas = despesas_qs.aggregate(total=Sum('valor_despesa'))['total'] or 0
        valor_total_vendas = vendas_qs.aggregate(total=Sum('valor_produto'))['total'] or 0

        # Status dos alunos (SEM FILTRO por período!)
        status_counts = {'em_dia': 0, 'quase_vencendo': 0, 'atrasado': 0, 'sem_dados': 0}
        for aluno in Aluno.objects.all():
            status = aluno.status_pagamento
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts['sem_dados'] += 1

        # Pagamentos por método (somente dentro do período)
        pagamentos_por_metodo = {
            metodo.metodo: (
                alunos_periodo.filter(metodo_pagamento=metodo).aggregate(total=Sum('valor_pago'))['total'] or 0
            ) + (
                vendas_qs.filter(metodo_pagamento=metodo).aggregate(total=Sum('valor_produto'))['total'] or 0
            )
            for metodo in MetodoPagamentoAluno.objects.all()
        }

        # Lucro
        lucro_bruto = total_pago_alunos + valor_total_vendas
        lucro_liquido = lucro_bruto - total_despesas

        # Gráfico de despesas por categoria
        despesas_por_categoria = (
            despesas_qs
            .values('nome__nome_despesa')
            .annotate(total=Sum('valor_despesa'))
            .order_by('-total')
        )
        categorias = [d['nome__nome_despesa'] for d in despesas_por_categoria]
        valores = [float(d['total']) for d in despesas_por_categoria]

        # Atualizando o contexto
        context.update({
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'total_alunos': Aluno.objects.count(),  # total geral
            'total_pago_alunos': total_pago_alunos,
            'total_geral_despesas': total_despesas,
            'total_despesas_count': despesas_qs.count(),
            'total_vendas': vendas_qs.count(),
            'valor_total_vendas': valor_total_vendas,
            **{f"alunos_{k}": v for k, v in status_counts.items()},
            'lucro_bruto': lucro_bruto,
            'lucro_liquido': lucro_liquido,
            'pagamentos_por_metodo': pagamentos_por_metodo,
            'categorias_despesas': categorias,
            'valores_despesas': valores,
        })
        return context



#### RELATÓRIOS PDF -----------------------------------------------------------------------

# Função para converter string para date de forma segura
def parse_date_safe(value):
    try:
        if value and value != "None":
            return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        pass
    return None

def exportar_relatorio_recebidos_pdf(request):
    # Pegando filtros e convertendo datas de forma segura
    data_inicio = parse_date_safe(request.GET.get('data_inicio'))
    data_fim = parse_date_safe(request.GET.get('data_fim'))
    metodo_pagamento_id = request.GET.get('metodo_pagamento')

    # Query base
    alunos = Aluno.objects.all().order_by('-data_pagamento')
    produtos = Produto.objects.all().order_by('-data_venda')

    # Aplicando filtros de data
    if data_inicio:
        alunos = alunos.filter(data_pagamento__gte=data_inicio)
        produtos = produtos.filter(data_venda__gte=data_inicio)
    if data_fim:
        alunos = alunos.filter(data_pagamento__lte=data_fim)
        produtos = produtos.filter(data_venda__lte=data_fim)

    # Aplicando filtro de método de pagamento apenas se válido
    if metodo_pagamento_id and metodo_pagamento_id.isdigit():
        alunos = alunos.filter(metodo_pagamento_id=int(metodo_pagamento_id))
        produtos = produtos.filter(metodo_pagamento_id=int(metodo_pagamento_id))

    # Totais
    total_pago_alunos = sum(a.valor_pago for a in alunos)
    total_pago_produtos = sum(p.valor_produto for p in produtos)
    total_geral = total_pago_alunos + total_pago_produtos

    # Contexto para o template
    context = {
        "alunos": alunos,
        "vendas": produtos,  # o template espera "vendas"
        "total_pago_alunos": f"{total_pago_alunos:,.2f}",
        "total_pago_vendas": f"{total_pago_produtos:,.2f}",
        "total_geral": f"{total_geral:,.2f}",
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "metodos_pagamento": [],  # se quiser, passe a lista real
        "metodo_pagamento_id": metodo_pagamento_id,
    }

    # Renderiza o template em HTML
    template = get_template('gestao/relatorio_receber_pdf.html')
    html = template.render(context)

    # Criar PDF
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar PDF", status=500)

    # Retorna como download
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio_receber.pdf"'
    return response


def exportar_relatorio_despesas_pdf(request):
    # Filtrando por data, se fornecidad
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    despesas = Despesa.objects.all().order_by('-data_despesa')

    if data_inicio:
        despesas = despesas.filter(data_despesa__gte=data_inicio)
    if data_fim:
        despesas = despesas.filter(data_despesa__lte=data_fim)

    total_geral = sum(d.valor_despesa for d in despesas)

    # Carrega o template HTML
    template_path = 'gestao/relatorio_despesa_pdf.html'
    context = {
        'despesas': despesas,
        'total_geral': total_geral,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    template = get_template(template_path)
    html = template.render(context)

    # Cria o PDF
    response = HttpResponse(content_type='application/pdf')
    data_hoje = datetime.today().strftime('%Y-%m-%d')
    response['Content-Disposition'] = f'inline; filename="relatorio_despesas_{data_hoje}.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF <pre>' + html + '</pre>')
    
    return response