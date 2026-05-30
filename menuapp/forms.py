from django import forms

from .models import Category, MenuItem


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = (
            'restaurant',
            'name',
            'name_tr',
            'name_en',
            'description',
            'description_tr',
            'description_en',
            'display_order',
        )

    def __init__(self, *args, **kwargs):
        venues = kwargs.pop('venues', None)
        super().__init__(*args, **kwargs)

        if venues is not None:
            self.fields['restaurant'].queryset = venues
            self.fields['restaurant'].label_from_instance = lambda venue: venue.name

        for field in self.fields.values():
            existing_classes = field.widget.attrs.get('class', '')

            if field.widget.__class__.__name__ == 'Select':
                field.widget.attrs['class'] = f'{existing_classes} form-select bg-dark text-white border-secondary'.strip()
            else:
                field.widget.attrs['class'] = f'{existing_classes} form-control bg-dark text-white border-secondary'.strip()


class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem
        fields = (
            'restaurant',
            'category',
            'title',
            'title_tr',
            'title_en',
            'description',
            'description_tr',
            'description_en',
            'price',
            'image',
            'is_available',
            'is_featured',
            'calories',
            'prep_time',
            'allergens',
            'ingredients',
        )
        widgets = {
            'allergens': forms.CheckboxSelectMultiple(),
            'ingredients': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        venues = kwargs.pop('venues', None)
        super().__init__(*args, **kwargs)

        self.fields['image'].required = False

        if venues is not None:
            self.fields['restaurant'].queryset = venues
            self.fields['restaurant'].label_from_instance = lambda venue: venue.name
            self.fields['category'].queryset = Category.objects.filter(
                restaurant__in=venues
            ).select_related('restaurant').order_by('restaurant__name', 'display_order', 'name')
            self.fields['category'].label_from_instance = lambda category: f'{category.restaurant.name} / {category.name}'

        for field_name, field in self.fields.items():
            if field_name in ('allergens', 'ingredients', 'is_available', 'is_featured'):
                continue

            existing_classes = field.widget.attrs.get('class', '')

            if field.widget.__class__.__name__ == 'Select':
                field.widget.attrs['class'] = f'{existing_classes} form-select bg-dark text-white border-secondary'.strip()
            else:
                field.widget.attrs['class'] = f'{existing_classes} form-control bg-dark text-white border-secondary'.strip()

        if restaurant:
            self.fields['restaurant'].initial = restaurant

            if venues is None:
                self.fields['category'].queryset = Category.objects.filter(
                    restaurant=restaurant
                ).order_by('display_order', 'name')

    def clean(self):
        cleaned_data = super().clean()
        restaurant = cleaned_data.get('restaurant')
        category = cleaned_data.get('category')

        if restaurant and category and category.restaurant_id != restaurant.id:
            self.add_error('category', 'Category must belong to the selected venue.')

        return cleaned_data
