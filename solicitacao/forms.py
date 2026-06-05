from django import forms
from django.forms import ModelForm

from solicitacao.models import SolicitacaoDeAdocao


class FormularioSolicitacao(ModelForm):
    class Meta:
        model = SolicitacaoDeAdocao
        fields = ['mensagem']
        labels = {
            'mensagem': 'Mensagem para o responsável',
        }
        help_texts = {
            'mensagem': 'Conte brevemente por que você quer adotar este pet.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mensagem'].widget.attrs.update({
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Ex.: Tenho interesse na adoção e gostaria de saber mais sobre a rotina do pet.',
        })


class FormularioAvaliacaoSolicitacao(ModelForm):
    class Meta:
        model = SolicitacaoDeAdocao
        fields = ['status']
        labels = {
            'status': 'Status da solicitação',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs['class'] = 'custom-select'
