from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'stocks', views.StockViewSet, basename='stock')
router.register(r'portfolios', views.PortfolioViewSet, basename='portfolio')
router.register(r'portfolio-stocks', views.PortfolioStockViewSet, basename='portfoliostock')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', views.public_dashboard, name='public_dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('portfolio/<int:portfolio_id>/order/', views.execute_order, name='execute_order'),
    path('portfolio/<int:portfolio_id>/order/<int:transaction_id>/modify/', views.modify_order, name='modify_order'),
    path('portfolio/<int:portfolio_id>/order/<int:transaction_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('portfolio/<int:portfolio_id>/edit/', views.edit_portfolio, name='edit_portfolio'),
    path('portfolio/<int:portfolio_id>/delete/', views.delete_portfolio, name='delete_portfolio'),
    path('api/', include(router.urls)),
]