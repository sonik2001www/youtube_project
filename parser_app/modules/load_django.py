import os
import sys
import django
from pathlib import Path


# sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
sys.path.append(os.path.abspath('youtube_project'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'youtube_project.settings'
django.setup()
