"""
Models for Product

All of the models are stored in this module
"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


# Function to initialize the database
def init_db(app):
    """Initializes the SQLAlchemy app"""
    Product.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Category(Enum):
    """Enumeration of valid Product Category"""

    ELECTRONICS = 0
    PERSONAL_CARE = 1
    TOYS = 2
    SPORTS = 3
    FOOD = 4
    HEALTH = 5
    OTHERS = 100


class Product(db.Model):
    """
    Class that represents a Product
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    image_url = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum(Category), nullable=True)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def to_dict(self):
        """Converts the Product instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "available": self.available,
            "image_url": self.image_url,
            "category": self.category.name,
        }

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "available": self.available,
            "image_url": self.image_url,
            "category": self.category.name,  # convert enum to string
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.description = data["description"]
            self.price = data["price"]
            self.description = data["description"]
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: "
                    + str(type(data["available"]))
                )
            self.image_url = data["image_url"]
            self.category = getattr(
                Category, data["category"]
            )  # create enum from string
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    def change_availability(self):
        """
        Changes the availability of the Product
        """
        self.available = not self.available
        db.session.commit()
        logger.info("Availability changed for %s", self.name)

    # # flake8: noqa: C901
    # def deserialize_update(self, data):
    #     """
    #     Deserializes a Product from a dictionary

    #     Args:
    #         data (dict): A dictionary containing the resource data
    #         it only contain keys of fields to be updated
    #     """
    #     try:
    #         if "name" in data:
    #             self.name = data["name"]
    #         if "description" in data:
    #             self.description = data["description"]
    #         if "price" in data:
    #             self.price = data["price"]
    #         if "description" in data:
    #             self.description = data["description"]
    #         if "available" in data:
    #             if isinstance(data["available"], bool):
    #                 self.available = data["available"]
    #             else:
    #                 raise DataValidationError(
    #                     "Invalid type for boolean [available]: "
    #                     + str(type(data["available"]))
    #                 )
    #         if "image_url" in data:
    #             self.image_url = data["image_url"]
    #         if "category" in data:
    #             self.category = getattr(
    #                 Category, data["category"]
    #             )  # create enum from string
    #     except AttributeError as error:
    #         raise DataValidationError("Invalid attribute: " + error.args[0]) from error
    #     return self

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the Product in the database"""
        logger.info("Processing all Product")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def find_or_404(cls, product_id: int):
        """Find a Product by it's id

        :param product_id: the id of the Product to find
        :type product_id: int

        :return: an instance with the product_id, or 404_NOT_FOUND if not found
        :rtype: Product

        """
        logger.info("Processing lookup or 404 for id %s ...", product_id)
        return cls.query.get_or_404(product_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Product with the given name

        Args:
            name (string): the name of the Product you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Products by their availability

        :param available: True for products that are available
        :type available: str

        :return: a collection of Products that are available
        :rtype: list

        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)

    @classmethod
    def find_by_category(cls, category: Category) -> list:
        """Returns all of the Pets in a category

        :param category: the category of the Pets you want to match
        :type category: Category Enum

        :return: a collection of Pets in that category
        :rtype: list

        """
        logger.info("Processing category query for %s ...", category)
        return cls.query.filter(cls.category == category)

    @classmethod
    def create_multiple_products(cls, products_data):
        """
        Adds multiple products to the database.
        :param products_data: List of dictionaries, where each dictionary contains data for one product.
        """
        products = []
        for data in products_data:
            product = cls(
                name=data["name"],
                description=data.get("description", None),
                price=data["price"],
                available=data["available"],
                image_url=data.get("image_url", None),
                category=data.get("category", None),
            )
            products.append(product)

        db.session.add_all(products)
        db.session.commit()
        return products
