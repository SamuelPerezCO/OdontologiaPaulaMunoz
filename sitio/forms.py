from django import forms

from .models import SolicitudCita, Tratamiento


class SolicitudCitaForm(forms.ModelForm):
    # Campo trampa: los formularios automatizados lo llenan, las personas no.
    # Se llama «apellido» para que resulte creíble; va oculto por CSS.
    apellido = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = SolicitudCita
        fields = ['nombre', 'telefono', 'tratamiento', 'mensaje']
        labels = {
            'nombre': 'Tu nombre',
            'telefono': 'Tu teléfono',
            'tratamiento': '¿Qué necesitas?',
            'mensaje': 'Cuéntanos algo más',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Nombre y apellido', 'autocomplete': 'name'}),
            'telefono': forms.TextInput(attrs={
                'placeholder': '300 000 0000', 'autocomplete': 'tel', 'inputmode': 'tel'}),
            'mensaje': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Opcional. Si te da miedo el odontólogo, este es buen momento para decirlo.'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tratamiento'].queryset = Tratamiento.objects.publicados()
        self.fields['tratamiento'].required = False
        self.fields['tratamiento'].empty_label = 'Todavía no sé'
        self.fields['mensaje'].required = False

    def clean_apellido(self):
        if self.cleaned_data.get('apellido'):
            raise forms.ValidationError('No pudimos enviar el formulario.')
        return ''

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        digitos = [c for c in telefono if c.isdigit()]
        if len(digitos) < 7:
            raise forms.ValidationError(
                'Escribe un teléfono con el que podamos devolverte la llamada.')
        return telefono
