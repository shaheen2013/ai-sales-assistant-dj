from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_yasg.utils import swagger_auto_schema

urlpatterns = [
    path(
        "access-token/",
        swagger_auto_schema(tags=["Authentication"], method="post")(
            TokenObtainPairView.as_view()
        ),
        name="token_obtain_pair",
    ),
    path("refresh-token/", TokenRefreshView.as_view(), name="token_refresh"),
]
