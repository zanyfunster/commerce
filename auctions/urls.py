from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("accounts/login/", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<int:listing_id>/listing", views.listing, name="listing"),
    path("<int:listing_id>/close", views.close, name="close"),
    path("<int:listing_id>/bid", views.bid, name="bid"),
    path("new", views.new, name="new"),
    path("browse", views.browse, name="browse"),
    path("category/<slug:slug>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path('watchlist_edit/<int:listing_id>', views.watchlist_edit, name='watchlist_edit')
]
