from typing import Any
from django.db.models.base import Model as Model
from django.views.generic import DetailView, UpdateView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.db import transaction
from django.urls import reverse_lazy
from .models import Profile
from. forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm, UserLoginForm

# Create your views here.

class ProfileDetailView(DetailView):
    model = Profile
    context_object_name = 'profile'
    template_name = 'accounts/profile_detail.html'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['title'] = f'Страница пользователя:{self.object.user.username}'
        return context
    

class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    
    def get_object(self, queryset=None) -> Model:
        return self.request.user.profile
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        if self.request.method == 'POST':
            context['user_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserUpdateForm(instance=self.request.user)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)
    
    def get_success_url(self) -> str:
        return reverse_lazy('profile_detail', kwargs={'slug': self.object.slug})


class UserRegisterView(SuccessMessageMixin, CreateView):
    form_class = UserRegisterForm
    success_url = reverse_lazy('accounts:home')
    template_name = 'accounts/user_register.html'
    success_message = 'Вы успешно зарегистрировались. Можете войти на сайт!'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация на сайте'
        return context
    
    
class UserLoginView(SuccessMessageMixin, LoginView):
    form_class =UserLoginForm
    template_name = 'accounts/user_login.html'
    next_page = 'blog:home'
    success_message = 'Добро пожаловать на сайт!'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['title'] = 'Авторизация на сайте'
        return context
    
    
class UserLogoutView(SuccessMessageMixin, LogoutView):
    next_page = 'blog:home'
    
