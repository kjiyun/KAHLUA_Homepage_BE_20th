from django.urls import path
from .views import image_view, ImageUploadView

urlpatterns = [
    path('photos/<str:image_name>/', image_view, name='image_view'),
    path('generate_presigned_url/', ImageUploadView.as_view({'post': 'generate_presigned_url'}), name='generate_presigned_url'),
]