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
    price = db.Column(db.Float)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    image_url = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum(Category), nullable=True)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

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
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data - "
                "Error message: " + error
            ) from error
        return self

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
    def find_by_name(cls, name):
        """Returns all Product with the given name

        Args:
            name (string): the name of the Product you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
