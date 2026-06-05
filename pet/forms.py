from django import forms
from django.forms import ModelForm
from pet.models import Pet
from user.consts import STATUS_ONG_APROVADA, TIPO_ONG
from user.models import User

class FormularioPet(ModelForm):
    class Meta:
        model = Pet
        fields = ['nome', 'especie', 'fotos', 'raca', 'idade', 'sexo', 'porte', 'vacinado', 'castrado', 'descricao', 'status', 'responsavel']
        labels = {
            'idade': 'Idade (meses)',
            'responsavel': 'Responsável pelo pet',
        }
        help_texts = {
            'idade': 'Informe a idade em meses. Exemplo: 6 para um filhote de 6 meses.',
            'sexo': 'Selecione uma opção.',
            'porte': 'Selecione uma opção.',
            'status': 'Selecione uma opção.',
            'responsavel': 'Selecione a ONG ou adotante responsável pelo contato.',
        }

    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        responsavel_field = self.fields.get('responsavel')

        if self.current_user and self.current_user.tipo_usuario == TIPO_ONG:
            self.fields.pop('responsavel')
        elif responsavel_field:
            responsavel_field.required = True
            responsavel_field.queryset = User.objects.filter(
                tipo_usuario=TIPO_ONG,
                status_verificacao_ong=STATUS_ONG_APROVADA,
            ).exclude(
                telefone__isnull=True,
            ).exclude(
                telefone=''
            ).order_by('nome')

        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css_class = 'custom-select'
            elif isinstance(field.widget, forms.FileInput):
                css_class = 'form-control-file'

            field.widget.attrs['class'] = css_class

            if field_name == 'descricao':
                field.widget.attrs.update({
                    'rows': 4,
                    'placeholder': 'Conte um pouco sobre o comportamento, rotina e necessidades do pet.',
                })
            elif field_name == 'nome':
                field.widget.attrs['placeholder'] = 'Ex.: Thor'
            elif field_name == 'especie':
                field.widget.attrs['placeholder'] = 'Ex.: Cachorro'
            elif field_name == 'raca':
                field.widget.attrs['placeholder'] = 'Ex.: Vira-lata'
