from django.db import models
from django.conf import settings

from team_finder.constants import (
    PROJECT_NAME_MAX_LEN,
    PROJECT_STATUS_MAX_LEN,
    PROJECT_STATUS_CHOICES,
    PROJECT_STATUS_OPEN,
)


class Project(models.Model):
    name = models.CharField(
        max_length=PROJECT_NAME_MAX_LEN, verbose_name="Название проекта"
    )
    description = models.TextField(blank=True, verbose_name="Описание проекта")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name="Автор проекта",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    github_url = models.URLField(blank=True, null=True, verbose_name="Ссылка на GitHub")
    status = models.CharField(
        max_length=PROJECT_STATUS_MAX_LEN,
        choices=PROJECT_STATUS_CHOICES,
        default=PROJECT_STATUS_OPEN,
        verbose_name="Статус проекта",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="participated_projects",
        verbose_name="Участники проекта",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
