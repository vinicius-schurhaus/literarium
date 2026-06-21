import os

from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.http import FileResponse
from django.views.static import serve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.api_urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]


def spa_index(request):
    """Serve o index.html do build do React para qualquer rota da SPA (deep links
    do React Router). Os assets com hash são servidos antes pelo WhiteNoise."""
    index = os.path.join(settings.BASE_DIR, "frontend", "dist", "index.html")
    return FileResponse(open(index, "rb"))


# Fallback da SPA — registrado por último e apenas quando o build existe (produção
# combinada). O negative-lookahead evita engolir respostas de API/admin/media.
if (settings.BASE_DIR / "frontend" / "dist" / "index.html").exists():
    urlpatterns += [re_path(r"^(?!api/|admin/|media/).*$", spa_index)]
