from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from functools import wraps

from .services import AdminService
from .forms import AdminLoginForm, UserStatusForm, ProductFilterForm, LinkFilterForm
from apps.users.services import UserService
from services.cosmos_db import CosmosDBService


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        request = args[0] if hasattr(args[0], 'session') else args[1]
        admin_user = request.session.get('admin_user')
        if not admin_user:
            return redirect('admin_dashboard:login')
        try:
            user = CosmosDBService.get_by_id('users', admin_user['id'], admin_user['id'])
            if user.get('role') != 'admin':
                request.session.pop('admin_user', None)
                return redirect('admin_dashboard:login')
        except Exception:
            request.session.pop('admin_user', None)
            return redirect('admin_dashboard:login')
        request.admin_user = user
        return view_func(*args, **kwargs)
    return wrapper


class AdminLoginView(View):
    template_name = 'admin_dashboard/login.html'

    def get(self, request):
        if request.session.get('admin_user'):
            return redirect('admin_dashboard:dashboard')
        form = AdminLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                user = UserService.authenticate(email, password)
                user_dict = user.to_dict()
                if user_dict.get('role') != 'admin':
                    messages.error(request, 'This account does not have admin privileges.')
                else:
                    request.session['admin_user'] = {
                        'id': user.id,
                        'email': user.email,
                        'display_name': user.display_name,
                    }
                    return redirect('admin_dashboard:dashboard')
            except Exception as e:
                messages.error(request, str(e))

        return render(request, self.template_name, {'form': form})


class AdminLogoutView(View):
    def post(self, request):
        request.session.pop('admin_user', None)
        return redirect('admin_dashboard:login')


class DashboardView(View):
    template_name = 'admin_dashboard/dashboard.html'

    @admin_required
    def get(self, request):
        stats = AdminService.get_dashboard_stats()
        return render(request, self.template_name, {
            'stats': stats,
            'admin_user': request.admin_user,
        })


class UserListView(View):
    template_name = 'admin_dashboard/users/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        users, total = AdminService.list_users(page)
        return render(request, self.template_name, {
            'users': users,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'admin_user': request.admin_user,
        })


class UserDetailView(View):
    template_name = 'admin_dashboard/users/detail.html'

    @admin_required
    def get(self, request, user_id):
        user = AdminService.get_user(user_id)
        if not user:
            messages.error(request, 'User not found.')
            return redirect('admin_dashboard:users')

        form = UserStatusForm(initial={'status': user.get('status', 'active')})
        return render(request, self.template_name, {
            'user': user,
            'form': form,
            'admin_user': request.admin_user,
        })

    @admin_required
    def post(self, request, user_id):
        form = UserStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            user = AdminService.update_user_status(user_id, status)
            if user:
                messages.success(request, f'User status updated to {status}.')
            else:
                messages.error(request, 'Failed to update user.')

        return redirect('admin_dashboard:user_detail', user_id=user_id)


class UserDeleteView(View):
    @admin_required
    def post(self, request, user_id):
        if AdminService.delete_user(user_id):
            messages.success(request, 'User deleted.')
        else:
            messages.error(request, 'Failed to delete user.')
        return redirect('admin_dashboard:users')


class ProductListView(View):
    template_name = 'admin_dashboard/products/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        form = ProductFilterForm(request.GET)
        shop_id = None
        if form.is_valid():
            shop_id = form.cleaned_data.get('shop_id')

        products, total = AdminService.list_products(page, shop_id=shop_id)
        return render(request, self.template_name, {
            'products': products,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'form': form,
            'admin_user': request.admin_user,
        })


class ProductDetailView(View):
    template_name = 'admin_dashboard/products/detail.html'

    @admin_required
    def get(self, request, product_id, shop_id):
        product = AdminService.get_product(product_id, shop_id)
        if not product:
            messages.error(request, 'Product not found.')
            return redirect('admin_dashboard:products')

        return render(request, self.template_name, {
            'product': product,
            'admin_user': request.admin_user,
        })


class ProductDeleteView(View):
    @admin_required
    def post(self, request, product_id, shop_id):
        if AdminService.delete_product(product_id, shop_id):
            messages.success(request, 'Product deleted.')
        else:
            messages.error(request, 'Failed to delete product.')
        return redirect('admin_dashboard:products')


class LinkListView(View):
    template_name = 'admin_dashboard/links/list.html'

    @admin_required
    def get(self, request):
        page = int(request.GET.get('page', 1))
        form = LinkFilterForm(request.GET)
        status = None
        if form.is_valid():
            status = form.cleaned_data.get('status')

        links, total = AdminService.list_links(page, status=status)
        return render(request, self.template_name, {
            'links': links,
            'total': total,
            'page': page,
            'total_pages': (total + 19) // 20,
            'form': form,
            'admin_user': request.admin_user,
        })


class LinkDetailView(View):
    template_name = 'admin_dashboard/links/detail.html'

    @admin_required
    def get(self, request, link_id, user_id):
        link = AdminService.get_link(link_id, user_id)
        if not link:
            messages.error(request, 'Link not found.')
            return redirect('admin_dashboard:links')

        return render(request, self.template_name, {
            'link': link,
            'admin_user': request.admin_user,
        })


class LinkRetryView(View):
    @admin_required
    def post(self, request, link_id, user_id):
        link = AdminService.retry_failed_link(link_id, user_id)
        if link:
            messages.success(request, 'Link queued for retry.')
        else:
            messages.error(request, 'Cannot retry this link.')
        return redirect('admin_dashboard:link_detail', link_id=link_id, user_id=user_id)


class LinkDeleteView(View):
    @admin_required
    def post(self, request, link_id, user_id):
        if AdminService.delete_link(link_id, user_id):
            messages.success(request, 'Link deleted.')
        else:
            messages.error(request, 'Failed to delete link.')
        return redirect('admin_dashboard:links')
