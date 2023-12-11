"""
Test cases for YourResourceModel Model

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Category, Product, DataValidationError, db
from service import app
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()
        db.drop_all()  # clean up test db

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a Product and assert that it exists"""
        product = Product(
            name="iPhone 15 Pro",
            description="Titanium. A17 Pro chip",
            price=999,
            available=True,
            category=Category.ELECTRONICS,
        )
        self.assertEqual(str(product), "<Product iPhone 15 Pro id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "iPhone 15 Pro")
        self.assertEqual(product.description, "Titanium. A17 Pro chip")
        self.assertEqual(product.price, 999)
        self.assertEqual(product.available, True)
        self.assertEqual(product.category, Category.ELECTRONICS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(
            name="iPhone 15 Pro",
            description="Titanium. A17 Pro chip",
            price=999,
            available=False,
            category=Category.ELECTRONICS,
        )
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_read_a_product(self):
        """It should Read a product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should Update a product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)
        # Change it an save it
        product.price = 100.00
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.price, 100.00)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].price, 100.00)

    def test_update_no_id(self):
        """It should not Update a product with no id"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_change_product_availability(self):
        """It should change the availability of a product"""
        # Create a product
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Check initial availability
        initial_availability = product.available
        # Change availability
        product.change_availability()
        self.assertNotEqual(product.available, initial_availability)
        # Fetch it back and verify the change
        updated_product = Product.find(product.id)
        self.assertEqual(updated_product.available, not initial_availability)

    def test_list_all_products(self):
        """It should List all products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_serialize_a_product(self):
        """It should serialize a product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)
        self.assertIn("available", data)
        self.assertEqual(data["available"], product.available)
        self.assertIn("image_url", data)
        self.assertEqual(data["image_url"], product.image_url)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category.name)

    def test_deserialize_a_product(self):
        """It should de-serialize a product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.available, data["available"])
        self.assertEqual(product.image_url, data["image_url"])
        self.assertEqual(product.category.name, data["category"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a product with missing data"""
        data = {"id": 1, "name": "Kitty", "price": 100}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["available"] = "true"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_category(self):
        """It should not deserialize a bad category attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["category"] = "xxx"  # wrong case
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    # def test_deserialize_update_a_product(self):
    #     """It should de-serialize-update a product"""
    #     data = ProductFactory().serialize()
    #     product = Product()
    #     product.deserialize_update(data)
    #     self.assertNotEqual(product, None)
    #     self.assertEqual(product.id, None)
    #     self.assertEqual(product.name, data["name"])
    #     self.assertEqual(product.description, data["description"])
    #     self.assertEqual(product.price, data["price"])
    #     self.assertEqual(product.available, data["available"])
    #     self.assertEqual(product.image_url, data["image_url"])
    #     self.assertEqual(product.category.name, data["category"])

    # def test_deserialize_update_bad_available(self):
    #     """It should not deserialize-update a bad available attribute"""
    #     test_product = ProductFactory()
    #     data = test_product.serialize()
    #     data["available"] = "true"
    #     product = Product()
    #     self.assertRaises(DataValidationError, product.deserialize_update, data)

    # def test_deserialize_update_bad_category(self):
    #     """It should not deserialize-update a bad category attribute"""
    #     test_product = ProductFactory()
    #     data = test_product.serialize()
    #     data["category"] = "xxx"  # wrong case
    #     product = Product()
    #     self.assertRaises(DataValidationError, product.deserialize_update, data)

    def test_find_product(self):
        """It should Find a product by ID"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(Product.all()), 5)
        # find the 2nd product in the list
        product = Product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.available, products[1].available)

    def test_find_by_name(self):
        """It should Find a product by Name"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should Find products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        # print(category)
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        products = ProductFactory.create_batch(3)
        for product in products:
            product.create()

        product = Product.find_or_404(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.available, products[1].available)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Product.find_or_404, 0)

    def test_create_multiple_products(self):
        """It should Create multiple products and add them to the database"""
        products = Product.all()
        self.assertEqual(products, [])

        # Create 5 products
        products_data = [ProductFactory().to_dict() for _ in range(5)]
        created_products = Product.create_multiple_products(products_data)

        products = Product.all()
        self.assertEqual(len(products), 5)

        # Check the correctness of data content
        for i, data in enumerate(products_data):
            product = products[i]
            self.assertIsNotNone(product.id)
            self.assertEqual(product.name, data["name"])
            self.assertEqual(product.description, data["description"])
            self.assertEqual(product.price, data["price"])
            self.assertEqual(product.available, data["available"])
            self.assertEqual(product.category.name, data["category"])

            self.assertEqual(created_products[i], product)
