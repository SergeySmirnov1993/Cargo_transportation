from django.urls import path

from transportation import views


urlpatterns = [
    path('', views.home_page, name='home-page'),
    path('orders', views.show_orders, name='orders'),
    path('transport', views.show_transport, name='transport'),
    path('drivers', views.show_drivers, name='drivers'),
    path('add-order', views.add_order, name='add-order'),
    path('add-transport', views.add_transport, name='add-transport'),
    path('add-additional-order/<int:order_id>', views.add_additional_order, name='additional-order'),
    path('edit-order/<int:order_id>', views.edit_order, name='edit-order'),
    path('edit-transport/<int:truck_id>', views.edit_transport, name='edit-transport'),
    path('edit-driver/<int:driver_id>', views.edit_driver, name='edit-driver'),
    path('delete-order/<int:order_id>', views.delete_order, name='delete-order'),
    path('delete-truck/<int:truck_id>', views.delete_truck, name='delete-truck'),
    path('delete-driver/<int:driver_id>', views.delete_driver, name='delete-driver'),
    path('completed-order/<int:order_id>', views.completed_order, name='completed-order'),
    path('charts', views.charts, name='charts'),
    path('reports', views.reports_dash, name='reports'),
    path('reports/<type>', views.reports_dash, name='reports'),
]
