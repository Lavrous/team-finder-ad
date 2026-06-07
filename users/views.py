from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm

from .forms import UserRegistrationForm, UserLoginForm, EditProfileForm
from .models import User
from team_finder.constants import USERS_PER_PAGE


def register_view(request):
    form = UserRegistrationForm(request.POST or None)

    if not form.is_valid():
        return render(request, "users/register.html", {"form": form})

    user = form.save()
    login(request, user)
    return redirect("projects:project_list")


def login_view(request):
    form = UserLoginForm(request.POST or None)

    if not form.is_valid():
        return render(request, "users/login.html", {"form": form})

    email = form.cleaned_data.get("email")
    password = form.cleaned_data.get("password")
    user = authenticate(request, email=email, password=password)

    if user is not None:
        login(request, user)
        next_url = request.GET.get("next", "projects:project_list")
        return redirect(next_url)

    form.add_error(None, "Неверный имейл или пароль")
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
    initial_data = {}
    if request.method == "GET":
        initial_data["skills"] = ", ".join([s.name for s in request.user.skills.all()])

    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
        initial=initial_data,
    )

    if not form.is_valid():
        return render(request, "users/edit_profile.html", {"form": form})

    form.save()
    return redirect("users:user_details", user_id=request.user.id)


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if not form.is_valid():
        return render(request, "users/change_password.html", {"form": form})

    form.save()
    update_session_auth_hash(request, form.user)
    return redirect("users:user_details", user_id=request.user.id)


def user_list(request):
    queryset = User.objects.all()

    active_filter = request.GET.get("filter")

    if request.user.is_authenticated and active_filter:
        filter_mapping = {
            "owners-of-favorite-projects": "owned_projects__in",
            "owners-of-participating-projects": "owned_projects__in",
            "interested-in-my-projects": "favorites__in",
            "participants-of-my-projects": "participated_projects__in",
        }

        filter_values = {
            "owners-of-favorite-projects": request.user.favorites.all(),
            "owners-of-participating-projects": request.user.participated_projects.all(),
            "interested-in-my-projects": request.user.owned_projects.all(),
            "participants-of-my-projects": request.user.owned_projects.all(),
        }

        if active_filter in filter_mapping:
            filter_kwarg = {filter_mapping[active_filter]: filter_values[active_filter]}
            queryset = queryset.filter(**filter_kwarg).distinct()

    paginator = Paginator(queryset, USERS_PER_PAGE)
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
