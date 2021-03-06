import traceback

from django.http.response import JsonResponse

from django.urls import reverse, reverse_lazy
from django.db.models.query import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import View, FormView, ListView, DetailView, CreateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.contrib import messages
from .models import Dataset, Image, ImageTransaction, Transaction
from .forms import ImageUploadForm


class ListView(LoginRequiredMixin, ListView):
    model = Dataset
    template_name = 'dataset/list.html'
    context_object_name = 'datasets'

    def get_queryset(self) -> QuerySet[Dataset]:
        """Only return datasets where user is owneer"""
        # queryset = super().get_queryset()
        # return queryset.filter(owner=self.request.user)
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        """Turn query into JSON"""
        context = super().get_context_data(**kwargs)
        context['datasets'] = [dataset for dataset in context['datasets'].values()]

        # Add url for every detailview for easy access on frontend
        for dataset in context['datasets']:
            dataset['detail_url'] = reverse('dataset:detail', kwargs={'pk': dataset['id']})
            dataset['delete_url'] = reverse('dataset:delete', kwargs={'pk': dataset['id']})
        return context

class DatasetDetailView(LoginRequiredMixin, DetailView):
    template_name = 'dataset/detail.html'
    model = Dataset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ImageUploadForm()
        context['transactions'] = ImageTransaction.objects.filter(dataset__id=self.kwargs['pk'])
        context['pk'] = self.kwargs['pk']
        context['urls'] = {'image_base': 'https://s3.eu-central-1.amazonaws.com/image-storage.dev.bucket/'}
        return context
    
class ImageUploadFormView(LoginRequiredMixin, SingleObjectMixin, FormView):
    template_name = 'dataset/detail.html'
    form_class = ImageUploadForm
    model = Dataset

    def post(self, request, pk, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            try:
                dataset = Dataset.objects.get(pk = pk)
            except Dataset.DoesNotExist:
                messages.add_message('Kritischer Fehler')
            else:
                try:
                    transaction = ImageTransaction.objects.create(dataset = dataset)
                except:
                    messages.add_message('Kritischer Fehler')
                else:
                    for file in files:
                        try:
                            image = Image.objects.create(file = file, dataset = dataset)
                        except Exception as e:
                            # TODO: Logging
                            messages.add_message(request, messages.WARNING, file.name + ' fehler beim upload aufgetreten.')
                        else:
                            transaction.images.add(image)
                            messages.add_message(request, messages.INFO, file.name + ' erfolgreich hochgeladen.')

                    transaction.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self) -> str:
        return reverse('dataset:detail', kwargs={'pk': self.object.pk})

class DetailView(View):
    
    def get(self, request, *args, **kwargs):
        view = DatasetDetailView.as_view()
        return view(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        view = ImageUploadFormView.as_view()
        return view(request, *args, **kwargs)

# Create your views here.
class CreateView(LoginRequiredMixin, CreateView):
    model = Dataset
    fields = ['name', 'description']
    template_name = 'dataset/create.html'

    def get_success_url(self) -> str:
        """Add owner to newly created dataset object"""
        object = self.object
        object.owner = self.request.user
        object.save()
        return reverse('dashboard:index') 

class DeleteView(LoginRequiredMixin, DeleteView):
    model = Dataset
    template_name = 'dataset/delete.html'
    success_url = reverse_lazy('dashboard:index')
