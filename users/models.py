from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone

from team_finder.constants import (
    USER_NAME_MAX_LEN,
    USER_SURNAME_MAX_LEN,
    USER_PHONE_MAX_LEN,
    USER_ABOUT_MAX_LEN,
)
from .managers import UserManager
from .utils import generate_avatar


class Skill(models.Model):
    name = models.CharField(
        max_length=50, unique=True, verbose_name="Название технологии"
    )

    class Meta:
        verbose_name = "Навык"
        verbose_name_plural = "Навыки"
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Адрес электронной почты")
    name = models.CharField(max_length=USER_NAME_MAX_LEN, verbose_name="Имя")
    surname = models.CharField(max_length=USER_SURNAME_MAX_LEN, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, verbose_name="Аватарка"
    )
    phone = models.CharField(
        max_length=USER_PHONE_MAX_LEN,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Номер телефона",
    )
    github_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на GitHub")
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LEN,
        blank=True,
        verbose_name="Описание профиля / О себе",
    )
    is_active = models.BooleanField(default=True, verbose_name="Активный аккаунт")
    is_staff = models.BooleanField(default=False, verbose_name="Доступ к админ-панели")

    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name="Дата регистрации"
    )

    skills = models.ManyToManyField(
        Skill, blank=True, related_name="users", verbose_name="Навыки"
    )
    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self.avatar = generate_avatar(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.surname}"
