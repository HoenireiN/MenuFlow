from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ('menu_item', 'customer_name', 'rating', 'comment')
        widgets = {
            'menu_item': forms.Select(attrs={
                'class': 'form-select bg-dark text-white border-secondary',
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control bg-dark text-white border-secondary',
            }),
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control bg-dark text-white border-secondary',
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control bg-dark text-white border-secondary',
            }),
        }

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)

        if restaurant:
            self.fields['menu_item'].queryset = restaurant.menuitem_set.filter(
                is_available=True
            ).order_by('category__display_order', 'title')

        self.fields['menu_item'].required = False
        self.fields['customer_name'].required = False

    def clean_rating(self):
        rating = self.cleaned_data['rating']

        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')

        return rating
