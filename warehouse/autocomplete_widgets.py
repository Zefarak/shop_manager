from dal import autocomplete
from .models import Employee

from django.utils.html import format_html


class EmployeeAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Employee.objects.none()
        qs = Employee.objects.filter(active=True)
        if self.q:
            qs = qs.filter(title__isstartswith=self.q)
        return qs