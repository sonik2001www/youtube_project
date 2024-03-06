from django.urls import path, include, re_path
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    path('', pars, name='pars'),
    path('profile/', user_profile, name='user_profile'),
    path('videos/', video_output, name='video_output'),
    path('channels/', channels_output, name='channels_output'),
    path('search/', search, name='search'),
    path('check/', check, name='check'),
    path('remove/', remove, name='remove'),
    path('load/videos/limit-<int:limit>-offset-<int:offset>/', load_videos),
    path('load/channels/limit-<int:limit>-offset-<int:offset>/', load_channels),
    path('tools/', tools, name='tools'),
    path('creator_overview/<str:channel_id>/', creator_overview, name='creator_overview'),
    path('libary_search/order_by=<str:sort_field>/', libary_search, name='libary_search'),
    path('pricing/', pricing, name='pricing'),
    path('support/', support, name='support'),
    path('delete_quota/', delete_quota, name='delete_quota'),
    path('delete_photo/', delete_photo, name='delete_photo'),
    path('add_remove/', add_remove, name='add_remove'),

    path('add_deal/', add_deal, name='add_deal'),
    path('deals/', deal, name='deals'),
    path('deals_archive/', deals_in_archive, name='deals_archive'),
    path('calendar/', calendar, name='calendar'),
    path('update_deal/<int:obj_id>/', update_deal, name='update_deal'),
    path('delete_deal/<int:obj_id>/', delete_deal, name='delete_deal'),
    path('clone_deal/<int:obj_id>/', clone_deal, name='clone_deal'),
    path('archive_deal/<int:obj_id>/', archive_deal, name='archive_deal'),
    path('archived_archive_deal/<int:obj_id>/', archived_archive_deal, name='archived_archive_deal'),

    path('invoice/',  invoice, name='invoice'),
    path('invoice_data/', invoice_data_view, name='invoice_data'), 

    # payments
    path('payment_manager', payment_redirect_view, name='payment_manager'),
    # Stripe payment urls
    path('stripe_create_checkout_session/', stripe_create_checkout_session_view, name='stripe_create_checkout_session'), 
    # Paypal payment urls
    path('paypal_create_checkout_session/', paypal_create_checkout_session_view, name='paypal_create_checkout_session'), 
    # Success payment
    path('success_payment/<str:plan>/<str:temp_token>/', success_payment_view, name='success_payment'), 

    # SALES
    path('tasks/', drug_and_door, name='drug_and_door'),
    path('update_column_positions/', update_column_positions, name='update_column_positions'),
    path('delete_column/', delete_column, name='delete_column'),
    path('move_field/', move_field, name='move_field'),
    path('delete_field/', delete_field, name='delete_field'),
    path('add_field/', add_field, name='add_field'),
    path('add_column/', add_column, name='add_column'),
    path('update_stars/', update_stars, name='update_stars'),

    # REMOVE VIDEO
    path('remove/<str:rem>', remove_item, name='remove_item'),


] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


