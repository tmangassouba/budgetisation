"""budgetisation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from importation import views as importer
from budgetiser import views as budget

urlpatterns = [
    # importer
    url(r'^$', importer.accueil, name='accueil'),
    url(r'^importer$', importer.importer, name='importer'),
    url(r'^import/files$', importer.files_view, name='files_list'),
    url(r'^import/files/(?P<id_file>[a-z\d]+)$', importer.file_view, name='file_cont'),
    url(r'^import/data$', importer.data_view, name='data_list'),
    url(r'^import/delete_file/(?P<id_file>[a-z\d]+)$', importer.delete_file, name='delete_file'),
    url(r'^import/edit_file/(?P<id_file>[a-z\d]+)$', importer.edit_file, name='edit_file'),
    # Budgetiser
    url(r'^budgetisation/analyse/$', budget.analyse_desciptive, name='analyse'),
    url(r'^budgetisation/prevision$', budget.prevision, name='prevision'),
]
