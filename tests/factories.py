# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""

import random
import factory
from faker import Faker
from factory.fuzzy import FuzzyChoice
from service.models import Category, Product


fake = Faker()


def product_name_provider():
    """Generate a product name"""
    adjectives = ["Eco", "Pro", "Ultra", "Mega", "Power", "Super"]
    product_types = ["Tool", "Device", "Apparatus", "Gadget", "Instrument", "Machine"]
    return f"{fake.random.choice(adjectives)} {fake.random.choice(product_types)}"


def product_description_provider():
    """Generate a product description"""
    adjectives = ["amazing", "incredible", "revolutionary", "innovative"]
    nouns = ["gadget", "device", "tool", "solution"]
    return f"This is an {fake.random.choice(adjectives)} {fake.random.choice(nouns)} for all your needs!"


def product_price_provider():
    """Generate a product price"""
    return round(fake.random_int(min=10, max=999) + 0.99, 2)


def product_image_url_provider():
    """Generate a product image_url"""
    return f"https://myimagehost.com/products/{fake.uuid4()}.jpg"


def product_category_provider():
    """Generate a product category"""
    return random.choice(list(Category))


class ProductFactory(factory.Factory):
    """Creates fake products that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.LazyFunction(product_name_provider)
    description = factory.LazyFunction(product_description_provider)
    price = factory.LazyFunction(product_price_provider)
    available = FuzzyChoice(choices=[True, False])
    image_url = factory.LazyFunction(product_image_url_provider)
    category = factory.LazyFunction(product_category_provider)


# product = ProductFactory()
# print(product.name)
# print(product.description)
# print(product.price)
# print(product.available)
# print(product.image_url)
# print(product.category)
