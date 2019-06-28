from django.views.generic import TemplateView


class RestaurantHomepageView(TemplateView):
    template_name = 'demo/index.html'