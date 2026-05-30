from django import forms

from .models import Restaurant


class VenueForm(forms.ModelForm):

    class Meta:
        model = Restaurant
        fields = (
            'name',
            'name_tr',
            'name_en',
            'venue_type',
            'description',
            'description_tr',
            'description_en',
            'logo',
            'opening_hours',
            'opening_time',
            'closing_time',
            'table_count',
            'theme_color',
            'is_manually_open',
            'is_active',
            'address',
            'phone',
            'email',
        )
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')

            input_type = getattr(field.widget, 'input_type', '')

            if field.widget.__class__.__name__ == 'Select':
                field.widget.attrs['class'] = f'{existing} form-select bg-dark text-white border-secondary'.strip()
            elif input_type in ('checkbox', 'file'):
                continue
            else:
                field.widget.attrs['class'] = f'{existing} form-control bg-dark text-white border-secondary'.strip()
