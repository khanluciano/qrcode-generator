import io
import sys
import base64
import os
from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.wsgi import get_wsgi_application
from django.shortcuts import render
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
import qrcode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    settings.configure(
        DEBUG=os.environ.get("DEBUG", "False") == "True",
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-key"),
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            'django.contrib.staticfiles',
        ],
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR],
            'APP_DIRS': False,
        }],
        MIDDLEWARE=[
            'django.middleware.common.CommonMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
        ],
        STATIC_URL='/static/',
        STATICFILES_DIRS=[os.path.join(BASE_DIR, "static")],
        STATIC_ROOT=os.path.join(BASE_DIR, "staticfiles"),
    )

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

MAX_LENGTH = 1000


@csrf_exempt
def generate_qr(request):
    context = {}
    if request.method == "POST":
        user_data = (request.POST.get('qr_link') or "").strip()

        if not user_data:
            context = {'error': "Please enter a link or text."}
        elif len(user_data) > MAX_LENGTH:
            context = {'error': f"Input is too long (max {MAX_LENGTH} characters)."}
        else:
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(user_data)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#ff5722", back_color="white")

            buffer = io.BytesIO()
            qr_img.save(buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            context = {
                'qr_code': f"data:image/png;base64,{img_base64}",
                'submitted_url': user_data,
            }

    return render(request, 'index.html', context)


urlpatterns = [
    path('', generate_qr, name='generate_qr'),
]
urlpatterns += staticfiles_urlpatterns()

application = get_wsgi_application()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["runserver", "127.0.0.1:8000"])
    execute_from_command_line(sys.argv)