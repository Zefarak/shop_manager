

def calculate_product_benefit_helper(self, instance, offer_type, value, discount_type):
    discount_value = 0
    if offer_type == 'SITE':
        discount_value = instance.final_value * (value / 100) if discount_type == 'Percentage' else \
            instance.order_items.count() * value if discount_type == 'Absolute' else value \
                if discount_type == 'Fixed Price' else 0
        if discount_type == 'Multibuy':
            order_item = instance.order_items.all().order_by('final_value').first()
            discount_value = order_item.final_value
    if offer_type == 'Categories':
        order_items = instance.order_items.all()
        for order_item in order_items:
            if order_item.product.category_site.all() in self.included_categories:
                if discount_type == 'Percentage':
                    discount_value += order_item.final_value * (value / 100)
                if discount_type == 'Absolute':
                    discount_value += value
                if discount_value == "Fixed Price":
                    discount_value = value
                    break
                if discount_value == 'Multibuy':
                    pass

    if offer_type == 'Brands':
        order_items = instance.order_items.all()
        for order_item in order_items:
            if order_item.product.brand in self.included_brands:
                if discount_type == 'Percentage':
                    discount_value += order_item.final_value * (value / 100)
                if discount_type == 'Absolute':
                    discount_value += value
                if discount_value == "Fixed Price":
                    discount_value = value
                    break
                if discount_value == 'Multibuy':
                    pass

    if offer_type == 'Products':
        order_items = instance.order_items.all()
        for order_item in order_items:
            if order_item.product in self.included_products:
                if discount_type == 'Percentage':
                    discount_value += order_item.final_value * (value / 100)
                if discount_type == 'Absolute':
                    discount_value += value
                if discount_value == "Fixed Price":
                    discount_value = value
                    break
                if discount_value == 'Multibuy':
                    pass
    return discount_value


