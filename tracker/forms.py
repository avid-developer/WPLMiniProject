from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import DailyTarget, MealEntry


class BootstrapMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            widget = field.widget
            css_class = 'form-control'

            if isinstance(widget, forms.Select):
                css_class = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)

            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css_class}'.strip()


class SignUpForm(BootstrapMixin, UserCreationForm):
    first_name = forms.CharField(max_length=150, label='Full name')
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('first_name', 'username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your name'
        self.fields['username'].widget.attrs['placeholder'] = 'Choose a username'
        self.fields['email'].widget.attrs['placeholder'] = 'you@example.com'
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'


class SignInForm(BootstrapMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        self.fields['username'].widget.attrs['placeholder'] = 'Enter your username'
        self.fields['password'].widget.attrs['placeholder'] = 'Enter your password'


class MealEntryForm(BootstrapMixin, forms.ModelForm):
    consumed_at = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            format='%Y-%m-%dT%H:%M',
            attrs={'type': 'datetime-local'},
        ),
    )

    class Meta:
        model = MealEntry
        fields = ('name', 'meal_type', 'quantity', 'unit', 'calories', 'consumed_at', 'notes')
        widgets = {
            'notes': forms.Textarea(attrs={'placeholder': 'Optional notes about the meal'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        self.fields['name'].widget.attrs['placeholder'] = 'Meal name'
        self.fields['quantity'].widget.attrs.update({'min': '0.25', 'step': '0.25'})
        self.fields['unit'].widget.attrs['placeholder'] = 'serving, bowl, glass...'
        self.fields['calories'].widget.attrs.update({'min': '1', 'step': '1'})
        self.fields['notes'].widget.attrs['placeholder'] = 'Optional notes'

        consumed_at = self.initial.get('consumed_at') or getattr(self.instance, 'consumed_at', None)
        if consumed_at:
            self.initial['consumed_at'] = timezone.localtime(consumed_at).strftime('%Y-%m-%dT%H:%M')
        else:
            self.initial['consumed_at'] = timezone.localtime().strftime('%Y-%m-%dT%H:%M')


class DailyTargetForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = DailyTarget
        fields = ('daily_target',)
        widgets = {
            'daily_target': forms.NumberInput(attrs={'min': '1200', 'max': '6000', 'step': '50'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class HistoryFilterForm(BootstrapMixin, forms.Form):
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Start date cannot be later than end date.')

        return cleaned_data
