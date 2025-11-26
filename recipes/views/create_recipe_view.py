# recipes/views/create_recipe_view.py

from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from recipes.models import Recipe
from recipes.forms.recipe_form import RecipeForm, IngredientFormSet, StepFormSet


class CreateRecipeView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "create_recipe.html"

    def _make_formsets(self, data=None):
        """
        Helper: construct both formsets with prefixes.
        """
        ingredient_formset = IngredientFormSet(
            data=data,
            prefix="ingredients",
        )
        step_formset = StepFormSet(
            data=data,
            prefix="steps",
        )
        return ingredient_formset, step_formset

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        ingredient_formset, step_formset = self._make_formsets()
        return self.render_to_response({
            "form": form,
            "ingredient_formset": ingredient_formset,
            "step_formset": step_formset,
        })

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        ingredient_formset, step_formset = self._make_formsets(request.POST)

        if "add_ingredient" in request.POST:
            data = request.POST.copy()
            total = int(data.get("ingredients-TOTAL_FORMS", 0))
            data["ingredients-TOTAL_FORMS"] = str(total + 1)
            ingredient_formset, step_formset = self._make_formsets(data)

            return self.render_to_response({
                "form": form,
                "ingredient_formset": ingredient_formset,
                "step_formset": step_formset,
            })

        if "add_step" in request.POST:
            data = request.POST.copy()
            total = int(data.get("steps-TOTAL_FORMS", 0))
            data["steps-TOTAL_FORMS"] = str(total + 1)
            ingredient_formset, step_formset = self._make_formsets(data)
            return self.render_to_response({
                "form": form,
                "ingredient_formset": ingredient_formset,
                "step_formset": step_formset,
            })

        if (
            form.is_valid()
            and ingredient_formset.is_valid()
            and step_formset.is_valid()
        ):
            return self._save_all(form, ingredient_formset, step_formset)

        return self.render_to_response({
            "form": form,
            "ingredient_formset": ingredient_formset,
            "step_formset": step_formset,
        })

    def _save_all(self, form, ingredient_formset, step_formset):
   
        form.instance.author = self.request.user
        self.object = form.save(commit=False)
        self.object.save()

        form.save_m2m()

        ingredient_formset.instance = self.object
        pos = 1
        for f in ingredient_formset.forms:
            if not f.cleaned_data or f.cleaned_data.get("DELETE"):
                continue
            f.instance.position = pos
            pos += 1
        ingredient_formset.save()

        step_formset.instance = self.object
        pos = 1
        for f in step_formset.forms:
            if not f.cleaned_data or f.cleaned_data.get("DELETE"):
                continue
            f.instance.position = pos
            pos += 1
        step_formset.save()

        messages.success(self.request, "Recipe added!")
        return self.redirect_success()

    def redirect_success(self):
        return self.render_to_response({
            "form": self.form_class(),
            "ingredient_formset": IngredientFormSet(prefix="ingredients"),
            "step_formset": StepFormSet(prefix="steps"),
        })
