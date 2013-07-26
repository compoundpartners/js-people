from django.http import HttpResponse
from django.views.generic import DetailView
from aldryn_people.models import Person


class DownloadVcardView(DetailView):
    model = Person

    def get(self, request, *args, **kwargs):
        person = self.get_object()
        filename = "%s.vcf" % person.name
        response = HttpResponse(person.get_vcard(), mimetype="text/x-vCard")
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response
