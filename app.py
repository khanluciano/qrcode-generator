import io
import sys
import base64
import os
from django.conf import settings
from django.core.management import execute_from_command_line
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
import qrcode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. CONFIGURE DJANGO RUNTIME SETTINGS (Must happen first!)
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="a_lively_secret_key_for_single_file_django",
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
        ],
        STATIC_URL='/static/',
        STATICFILES_DIRS=[BASE_DIR],
    )

# 2. NOW IT IS SAFE TO IMPORT DJANGO UTILITIES
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # <-- MOVED HERE

# 3. BACKEND VIEW LOGIC
@csrf_exempt
def generate_qr(request):
    context = {}
    if request.method == "POST":
        user_data = request.POST.get('qr_link')
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(user_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="#ff5722", back_color="white")
        
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        qr_data_url = f"data:image/png;base64,{img_base64}"
        
        context = {
            'qr_code': qr_data_url,
            'submitted_url': user_data
        }

    return render(request, 'index.html', context)

# 4. URL ROUTING
urlpatterns = [
    path('', generate_qr, name='generate_qr'),
 ]

# 5. APPEND STATIC FILE ROUTING MECHANISM
urlpatterns += staticfiles_urlpatterns()

# 6. SERVER RUNTIME LAUNCHER
if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(["runserver", "127.0.0.1:8000"])
    execute_from_command_line(sys.argv)
