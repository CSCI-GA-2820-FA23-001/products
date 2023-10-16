"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, abort
from service.common import status  # HTTP Status Codes
from service.models import Product

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    data = {
        "service_name": "Product Service",
        "description": "This service provides products for a catalog (id, name, description, price. etc.).",
        "endpoints": [
            {
                "path": "/products",
                "description": "Returns all the products in the database (can be filtered by a query string)",
                "methods": ["GET"],
            },
            {
                "path": "/products",
                "description": "Create a new product.",
                "methods": ["POST"],
            },
            {
                "path": "/products/<int:product_id>",
                "description": "Update fields of a existing product",
                "methods": ["PUT"],
            },
            {
                "path": "/products/<int:product_id>",
                "description": "Delete a Product based on the id specified in the path",
                "methods": ["DELETE"],
            },
        ],
    }
    return jsonify(data), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Products"""
    app.logger.info("Request for product list")
    products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# ADD A NEW PRODUCT
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    """
    Creates a Product
    This endpoint will create a Product based the data in the body that is posted
    """
    app.logger.info("Request to create a product")
    check_content_type("application/json")
    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    # TO-DO: Update location_url once Read is implemented
    # location_url = url_for("get_products", product_id=product.id, _external=True)
    location_url = "TO BE UPDATED"
    app.logger.info("Product with ID [%s] created.", product.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """
    Update a Product
    This endpoint will update a existing Product based the data in the body that is posted
    or return 404 there is no product with id provided in payload
    """

    app.logger.info("Request to update a product")
    check_content_type("application/json")

    product: Product = Product.find(product_id)
    if not product:
        app.logger.info("Invalid product id: %s", product_id)
        abort(
            status.HTTP_404_NOT_FOUND, f"There is no exist product with id {product_id}"
        )
    product.deserialize_update(request.get_json())
    product.update()
    message = product.serialize()

    return jsonify(message), status.HTTP_200_OK


# DELETE A PRODUCT
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to delete product with id: %s", product_id)
    product = Product.find(product_id)
    if product:
        product.delete()

    app.logger.info("Product with ID [%s] delete complete.", product_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )
