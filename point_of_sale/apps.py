from django.apps import AppConfig


class PointOfSaleConfig(AppConfig):
    name = 'point_of_sale'

    def ready(self):
        import point_of_sale.signals
