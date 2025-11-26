from django import forms
from django.forms import inlineformset_factory
from recipes.models import Recipe, RecipeIngredient, RecipeStep

class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = [
            'name', 'description' , 'serves' , 'difficulty', 
            'prepTime', 'cookTime', 'cuisine', 'visibility', 'tags'
        ]
        

IngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    fields =["text"],
    extra=1,
    can_delete=True

)

StepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    fields =["text"],
    extra=1,
    can_delete=True

)
         
