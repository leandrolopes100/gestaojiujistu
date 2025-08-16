from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from datetime import date, timedelta
from django.conf import settings

class GraduacaoAluno(models.Model):
    faixa = models.CharField(max_length=6, verbose_name="Faixa")

    def __str__(self):
        return self.faixa
    
class GeneroAluno(models.Model):
    genero = models.CharField(max_length=9, verbose_name="Genero")

    def __str__(self):
        return self.genero

class PagamentoAluno(models.Model):
    pagamento = models.CharField(max_length=15, verbose_name="Mensal ou Plano") #Mensal ou Plano

    def __str__(self):
        return self.pagamento
    
class MetodoPagamentoAluno(models.Model):
    metodo = models.CharField(max_length=15, verbose_name="Método de pagamento Aluno" ) #Pix, Débido, Crédito
    def __str__(self):
        return self.metodo
    
class TipoTurmaAluno(models.Model):
    categoria_etaria = models.CharField(max_length=10, verbose_name="Categoria Etária" )
    def __str__(self):
        return self.categoria_etaria
    

class Aluno(models.Model):
    nome = models.CharField(max_length=100, db_index=True, verbose_name="Nome")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    data_nascimento = models.DateField(db_index=True, blank=True, null=True, verbose_name="Data de Nascimento")
    telefone = PhoneNumberField(region='BR', verbose_name="Telefone de Contato")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.CharField(max_length=100, blank=True, null=True, verbose_name="Endereço")
    grupo_idade = models.ForeignKey(TipoTurmaAluno, null=True, on_delete=models.PROTECT, verbose_name="Categoria Etária")
    faixa_aluno = models.ForeignKey(GraduacaoAluno, db_index=True, on_delete=models.PROTECT, verbose_name="Faixa")
    data_cadastro = models.DateTimeField(auto_now_add=True)
    genero_aluno = models.ForeignKey(GeneroAluno, null=True, on_delete=models.PROTECT, verbose_name="Gênero")
    pagamento_aluno = models.ForeignKey(PagamentoAluno, null=True, on_delete=models.PROTECT, verbose_name="Mensal ou Plano")
    metodo_pagamento = models.ForeignKey(MetodoPagamentoAluno, null=True, on_delete=models.PROTECT, verbose_name="Método de Pagamento")
    valor_pago = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Valor Pago")
    data_pagamento = models.DateField(blank=True, null=True, verbose_name="Data de Pagamento")
    proximo_pagamento = models.DateField(blank=True, null=True, editable=False, verbose_name="Próximo Pagamento")  # <== NOVO CAMPO
    foto = models.ImageField(upload_to='foto_aluno/', blank=True, null=True)
    cadastrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, editable=False, verbose_name="Cadastrado por")

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.upper()

        if self.data_pagamento and self.pagamento_aluno:
            if self.pagamento_aluno.pagamento == "Mensal":
                self.proximo_pagamento = self.data_pagamento + timedelta(days=30)
            elif self.pagamento_aluno.pagamento == "Trimestral":
                self.proximo_pagamento = self.data_pagamento + timedelta(days=90)
            elif self.pagamento_aluno.pagamento == "Semestral":
                self.proximo_pagamento = self.data_pagamento + timedelta(days=180)
            elif self.pagamento_aluno.pagamento == "Anual":
                self.proximo_pagamento = self.data_pagamento + timedelta(days=365)
            else:
                self.proximo_pagamento = None
        else:
            self.proximo_pagamento = None
        super().save(*args, **kwargs)

    @property
    def status_pagamento(self):
        hoje = date.today()
        if self.proximo_pagamento:
            if self.proximo_pagamento < hoje:
                return 'atrasado'
            elif (self.proximo_pagamento - hoje).days <= 5:
                return 'quase_vencendo'
            else:
                return 'em_dia'
        return 'sem_dados'

    def __str__(self):
        return self.nome

class Produto(models.Model):
    nome_produto = models.CharField(max_length=100, verbose_name="Descrição")
    valor_produto = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Valor")
    data_venda = models.DateField(auto_now_add=True, editable=False)
    metodo_pagamento = models.ForeignKey(MetodoPagamentoAluno, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return self.nome_produto
    

class DespesaMensal(models.Model):
    nome_despesa = models.CharField(max_length=100, verbose_name="Descrição despesa")

    def __str__(self):
        return self.nome_despesa
    
class Despesa(models.Model):
    nome = models.ForeignKey(DespesaMensal, on_delete=models.PROTECT, verbose_name="Despesa")
    valor_despesa = models.DecimalField(max_digits=8, decimal_places=2, default=0, verbose_name="Valor")
    data_despesa = models.DateField(auto_now_add=True)