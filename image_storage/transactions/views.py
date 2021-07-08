from django.urls import reverse_lazy
from django.views.generic import DeleteView

from .models import ImageTransaction
# Create your views here.

class DeleteView(DeleteView):
    model = ImageTransaction
    template_name = 'transactions/delete.html'

    def get_success_url(self) -> str:
        return reverse_lazy('datasets:detail', kwargs={'pk': self.object.dataset.id})