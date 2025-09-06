from django import forms
from .models import Aluno, GeneroAluno, GraduacaoAluno, PagamentoAluno, TipoTurmaAluno, MetodoPagamentoAluno, Produto, Despesa

class AlunoForm(forms.ModelForm):
        class Meta:
            model = Aluno
            exclude = ['data_cadastro']
            widgets = {
                'nome': forms.TextInput(attrs={'placeholder': 'Nome Completo', 'class': 'form-control'}),
                'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                'telefone': forms.TextInput(attrs={'placeholder': '(99) 99999-9999', 'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'placeholder': 'exemplo@email.com', 'class': 'form-control'}),
                'endereco': forms.TextInput(attrs={'class': 'form-control'}),
                'valor_pago': forms.NumberInput(attrs={'placeholder': 'Valor', 'class': 'form-control'}),
                'cpf': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '000.000.000-00'}),
                'data_pagamento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            }   
        

class GeneroAlunoForm(forms.ModelForm): # Só no Painel ADM
    class Meta:
        model = GeneroAluno
        fields = '__all__'

class GraduacaoAlunoForm(forms.ModelForm): # Só no Painel ADM
    class Meta:
        model = GraduacaoAluno
        fields = '__all__'

class PagamentoAlunoForm(forms.ModelForm): # Só no Painel ADM
    class Meta:
        model = PagamentoAluno
        fields = '__all__'

class TipoAlunoForm(forms.ModelForm): # Só no Painel ADM
    class Meta:
        model = TipoTurmaAluno
        fields = '__all__'

class MetodoPagamentoForm(forms.ModelForm): # Só no Painel ADM
    class Meta:
        model = MetodoPagamentoAluno
        fields = '__all__'

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome_produto', 'valor_produto', 'quantidade', 'metodo_pagamento']
        widgets = {
            'nome_produto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite a descrição do produto'
            }),
            'valor_produto': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o valor unitário'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '999',
                'placeholder': 'Quantidade'
            }),
            'metodo_pagamento': forms.Select(attrs={
                'class': 'form-control select2'
            }),
        }

        
class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = '__all__'
        widgets = {
            'data_despesa': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white'
            }),
        }