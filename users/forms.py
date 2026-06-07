import re

from django import forms
from django.contrib.auth import get_user_model

from .models import Skill
from team_finder.validators import validate_github_url

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ["name", "surname", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )
    password = forms.CharField(label="Пароль", strip=False, widget=forms.PasswordInput)


class EditProfileForm(forms.ModelForm):
    skills = forms.CharField(required=False, help_text="Введите навыки через запятую")

    class Meta:
        model = User
        fields = ["name", "surname", "avatar", "about", "phone", "github_url", "skills"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return phone

        if not re.match(r"^(8|\+7)\d{10}$", phone):
            raise forms.ValidationError(
                "Формат телефона должен быть 8XXXXXXXXXX или +7XXXXXXXXXX"
            )

        if phone.startswith("8"):
            phone = "+7" + phone[1:]

        if User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Пользователь с таким номером телефона уже существует."
            )

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        validate_github_url(url)
        return url

    def clean_skills(self):
        skills_str = self.cleaned_data.get("skills", "")
        if not skills_str:
            return Skill.objects.none()

        skill_names = [s.strip() for s in skills_str.split(",") if s.strip()]
        skill_objs = []
        for name in skill_names:
            obj, _ = Skill.objects.get_or_create(name=name)
            skill_objs.append(obj)

        return skill_objs
