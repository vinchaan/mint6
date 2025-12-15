# recipes/forms/follow_form.py

from django import forms
from recipes.models import RecipeRating


class FollowUserForm(forms.ModelForm):
    class Meta:
        model = RecipeRating
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'class': 'form-control',
                'type': 'number'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Write your review (optional)...'
            })
        }
        labels = {
            'rating': 'Rating (1-5 stars)',
            'comment': 'Review'
        }
        help_texts = {
            'rating': 'Rate this recipe from 1 to 5 stars',
            'comment': 'Share your thoughts about this recipe (optional)'
        }


