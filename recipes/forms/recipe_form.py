# recipes/forms/recipe_form.py

from django import forms
from django.forms import inlineformset_factory
from recipes.models import Recipe, RecipeIngredient, RecipeStep, Tag


class RecipeForm(forms.ModelForm):    
    tags = forms.ModelMultipleChoiceField(
    queryset=Tag.objects.all().order_by('name'),
    required=False,
    widget=forms.CheckboxSelectMultiple,
    help_text="Select all tags that apply to this recipe"
    )
    
    class Meta:
        model = Recipe
        fields = [
            'name',
            'description',
            'serves',
            'difficulty',
            'prepTime',
            'cookTime',
            'cuisine',
            'visibility',
            'tags',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'prepTime': forms.TimeInput(attrs={'type': 'time'}),
            'cookTime': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields['tags'].initial = self.instance.tags.all()


class IngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'e.g., 200g pasta',
                'class': 'form-control'
            })
        }


class StepForm(forms.ModelForm):    
    class Meta:
        model = RecipeStep
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Describe this step...',
                'class': 'form-control',
                'rows': 3
            })
        }

IngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=IngredientForm,
    extra=1,
    can_delete=True,
)

StepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    form=StepForm,
    extra=1,
    can_delete=True,
)