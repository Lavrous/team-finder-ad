from http import HTTPStatus
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Project
from .forms import ProjectForm
from team_finder.constants import (
    PROJECT_STATUS_OPEN,
    PROJECT_STATUS_CLOSED,
    PROJECTS_PER_PAGE,
)
from team_finder.paginator import get_paginated_page


def project_list(request):
    projects = Project.objects.all()
    page_obj = get_paginated_page(request, projects, PROJECTS_PER_PAGE)

    context = {
        "projects": page_obj,
        "project_list": page_obj,
        "page_obj": page_obj,
    }
    return render(request, "projects/project_list.html", context)


def project_details(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)

    if not form.is_valid():
        return render(
            request, "projects/create-project.html", {"form": form, "is_edit": False}
        )

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect("projects:project_details", project_id=project.id)


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return redirect("projects:project_details", project_id=project.id)

    form = ProjectForm(request.POST or None, instance=project)

    if not form.is_valid():
        return render(
            request, "projects/create-project.html", {"form": form, "is_edit": True}
        )

    form.save()
    return redirect("projects:project_details", project_id=project.id)


@login_required
def favorite_projects(request):
    projects = request.user.favorites.all()

    context = {
        "projects": projects,
        "project_list": projects,
        "page_obj": projects,
    }
    return render(request, "projects/favorite_projects.html", context)


@login_required
@require_POST
def toggle_favorite(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    is_favorited = request.user.favorites.filter(id=project.id).exists()

    if is_favorited:
        request.user.favorites.remove(project)
    else:
        request.user.favorites.add(project)

    return JsonResponse({"status": "ok", "favorited": not is_favorited})


@login_required
@require_POST
def toggle_participate(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    is_participant = project.participants.filter(id=request.user.id).exists()

    if is_participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not is_participant})


@login_required
@require_POST
def complete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return JsonResponse(
            {
                "status": "error",
                "message": "Отказано в доступе. Вы не являетесь автором этого проекта.",
            },
            status=HTTPStatus.FORBIDDEN,
        )

    if project.status != PROJECT_STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "message": "Проект уже был завершен ранее."},
            status=HTTPStatus.BAD_REQUEST,
        )

    project.status = PROJECT_STATUS_CLOSED
    project.save()

    return JsonResponse({"status": "ok", "project_status": PROJECT_STATUS_CLOSED})
