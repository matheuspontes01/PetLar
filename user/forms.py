from django import forms
from django.forms import ModelForm
from user.consts import *
from user.models import User


class FormularioUser(ModelForm):
    TIPOS_SELECIONAVEIS = (
        (TIPO_ADOTANTE, 'Adotante'),
        (TIPO_ONG, 'ONG'),
    )

    class Meta:
        model = User
        fields = [
            'nome',
            'email',
            'senha',
            'telefone',
            'tipo_usuario',
            'razao_social_ong',
            'cnpj_ong',
            'comprovante_ong',
            'status_verificacao_ong',
        ]
        labels = {
            'razao_social_ong': 'Razão social',
            'cnpj_ong': 'CNPJ',
            'comprovante_ong': 'Comprovante da ONG',
            'status_verificacao_ong': 'Verificação da ONG',
        }
        help_texts = {
            'comprovante_ong': 'Envie um documento que comprove a atuação da ONG, como cartão CNPJ, estatuto ou declaração.',
            'status_verificacao_ong': 'Somente ONGs aprovadas podem cadastrar pets para adoção.',
        }

    def __init__(self, *args, **kwargs):
        self.require_ong_documents = kwargs.pop('require_ong_documents', False)
        self.show_verification_status = kwargs.pop('show_verification_status', True)
        super().__init__(*args, **kwargs)
        tipo_usuario_field = self.fields['tipo_usuario']
        tipo_usuario_field.choices = list(self.TIPOS_SELECIONAVEIS)

        if not self.show_verification_status:
            self.fields.pop('status_verificacao_ong')

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'custom-select'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control-file'
            else:
                field.widget.attrs['class'] = 'form-control'

        self.fields['nome'].widget.attrs['placeholder'] = 'Nome completo'
        self.fields['email'].widget.attrs['placeholder'] = 'voce@email.com'
        self.fields['telefone'].widget.attrs['placeholder'] = '(63) 99999-9999'
        self.fields['razao_social_ong'].widget.attrs['placeholder'] = 'Nome registrado da ONG'
        self.fields['cnpj_ong'].widget.attrs['placeholder'] = '00.000.000/0000-00'
        self.fields['senha'].widget = forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite uma senha segura',
        })

    def clean_cnpj_ong(self):
        cnpj = self.cleaned_data.get('cnpj_ong')
        if not cnpj:
            return cnpj

        digitos = ''.join(ch for ch in cnpj if ch.isdigit())
        if len(digitos) != 14 or len(set(digitos)) == 1:
            raise forms.ValidationError('Informe um CNPJ válido.')

        def calcular_digito(base, pesos):
            soma = sum(int(numero) * peso for numero, peso in zip(base, pesos))
            resto = soma % 11
            return '0' if resto < 2 else str(11 - resto)

        primeiro = calcular_digito(digitos[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
        segundo = calcular_digito(digitos[:12] + primeiro, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])

        if digitos[-2:] != primeiro + segundo:
            raise forms.ValidationError('Informe um CNPJ válido.')

        return cnpj

    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')

        if tipo_usuario == TIPO_ONG and self.require_ong_documents:
            for field_name in ['razao_social_ong', 'cnpj_ong', 'comprovante_ong']:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'Este campo é obrigatório para cadastro de ONG.')

        return cleaned_data
        
