from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegistrationForm, UserLoginForm, EditProfileForm
from .models import User, Skill


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:project_list")
    else:
        form = UserRegistrationForm()
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next") or "projects:project_list"
                return redirect(next_url)
            else:
                form.add_error(None, "Неверный имейл или пароль")
    else:
        form = UserLoginForm()
    return render(request, "users/login.html", {"form": form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("projects:project_list")


def user_details(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, "users/user-details.html", {"user": user})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = EditProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:user_details", user_id=request.user.id)
    else:
        skills_str = ", ".join([s.name for s in request.user.skills.all()])
        form = EditProfileForm(instance=request.user, initial={"skills": skills_str})
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("users:user_details", user_id=request.user.id)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})


def user_list(request):
    queryset = User.objects.all().order_by("-id")

    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        if active_filter == "owners-of-favorite-projects":
            queryset = queryset.filter(
                owned_projects__in=request.user.favorites.all()
            ).distinct()

        elif active_filter == "owners-of-participating-projects":
            queryset = queryset.filter(
                owned_projects__in=request.user.participated_projects.all()
            ).distinct()

        elif active_filter == "interested-in-my-projects":
            queryset = queryset.filter(
                favorites__in=request.user.owned_projects.all()
            ).distinct()

        elif active_filter == "participants-of-my-projects":
            queryset = queryset.filter(
                participated_projects__in=request.user.owned_projects.all()
            ).distinct()

    paginator = Paginator(queryset, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    query_prefix = f"filter={active_filter}&" if active_filter else ""

    context = {
        "participants": page_obj,
        "users": page_obj,
        "user_list": page_obj,
        "page_obj": page_obj,
        "active_filter": active_filter,
        "query_prefix": query_prefix,
    }
    return render(request, "users/participants.html", context)
