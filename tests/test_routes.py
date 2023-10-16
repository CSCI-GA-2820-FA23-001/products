"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from service import app
from service.models import db, init_db, Product
from service.common import status  # HTTP Status Codes
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)

BASE_URL = "/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], test_product.price)
        self.assertEqual(new_product["available"], test_product.available)
        self.assertEqual(new_product["image_url"], test_product.image_url)
        self.assertEqual(new_product["category"], test_product.category.name)

        # TO-DO: Check that the location header was correct

        # response = self.client.get(location)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # new_product = response.get_json()
        # self.assertEqual(new_product["name"], test_product.name)
        # self.assertEqual(new_product["description"], test_product.description)
        # self.assertEqual(new_product["price"], test_product.price)
        # self.assertEqual(new_product["available"], test_product.available)
        # self.assertEqual(new_product["image_url"], test_product.image_url)
        # self.assertEqual(new_product["category"], test_product.category.name)

    def test_update_product(self):
        """It should update a Product"""

        # create a product
        test_product_original = ProductFactory()
        logging.debug("Test Product: %s", test_product_original.serialize())
        response = self.client.post(BASE_URL, json=test_product_original.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()

        # update
        test_product_new = ProductFactory()
        test_product_new.id = new_product["id"]
        logging.debug("Test Product: %s", test_product_new.serialize())
        response = self.client.put(
            f"{BASE_URL}/{test_product_new.id}", json=test_product_new.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product_new.name)
        self.assertEqual(new_product["description"], test_product_new.description)
        self.assertEqual(new_product["price"], test_product_new.price)
        self.assertEqual(new_product["available"], test_product_new.available)
        self.assertEqual(new_product["image_url"], test_product_new.image_url)
        self.assertEqual(new_product["category"], test_product_new.category.name)

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted

        # remove comment block when read is implemented
        # response = self.client.get(f"{BASE_URL}/{test_product.id}")
        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_product_no_data(self):
        """It should not Create a Product with missing data"""
        response = self.client.post(BASE_URL, json={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with the wrong content type"""
        response = self.client.post(BASE_URL, data="hello", content_type="text/html")
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_available(self):
        """It should not Create a Product with bad available data"""
        test_product = ProductFactory()
        logging.debug(test_product)
        # change available to a string
        test_product.available = "true"
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_category(self):
        """It should not Create a Product with bad category data"""
        product = ProductFactory()
        logging.debug(product)
        # change category to a bad string
        test_product = product.serialize()
        test_product["category"] = "others"  # wrong case
        response = self.client.post(BASE_URL, json=test_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_missing_product(self):
        """It should not update a Product"""

        # create a product
        test_product_original = ProductFactory()
        logging.debug("Test Product: %s", test_product_original.serialize())
        response = self.client.post(BASE_URL, json=test_product_original.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_product = response.get_json()

        # update
        test_product_new = ProductFactory()
        test_product_new.id = new_product["id"] + 1
        logging.debug("Test Product: %s", test_product_new.serialize())
        response = self.client.put(
            f"{BASE_URL}/{test_product_new.id}", json=test_product_new.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
