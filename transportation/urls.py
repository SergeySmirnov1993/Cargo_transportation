from django.urls import path

from transportation import views


urlpatterns = [
    path('', views.home_page, name='home-page'),
    path('orders', views.show_orders, name='orders'),
    path('transport', views.transport, name='transport'),
    path('reports', views.reports, name='reports'),
    path('add-order', views.add_order, name='add-order'),
    path('edit-order/<int:order_id>', views.edit_order, name='edit-order'),
    path('delete-order/<int:order_id>', views.delete_order, name='delete-order'),
    path('add-transport', views.add_transport, name='add-transport'),
    path('edit-transport/<int:truck_id>', views.edit_transport, name='edit-transport'),
    path('delete-truck/<int:truck_id>', views.delete_truck, name='delete-truck'),
    path('completed-order/<int:order_id>', views.completed_order, name='completed-order'),
    path('add-additional-order/<int:order_id>', views.add_additional_order, name='additional-order'),
]
