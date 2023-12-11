"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, abort
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Product, Category, db

# Import Flask application
from . import app, api


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    # data = {
    #     "service_name": "Product Service",
    #     "description": "This service provides products for a catalog (id, name, description, price. etc.).",
    #     "endpoints": [
    #         {
    #             "path": "/products",
    #             "description": "Returns all the products in the database (can be filtered by a query string)",
    #             "methods": ["GET"],
    #         },
    #         {
    #             "path": "/products",
    #             "description": "Create a new product.",
    #             "methods": ["POST"],
    #         },
    #         {
    #             "path": "/products/collect",
    #             "description": "Create multiple Products.",
    #             "methods": ["POST"],
    #         },
    #         {
    #             "path": "/products/<int:product_id>",
    #             "description": "Update fields of a existing product",
    #             "methods": ["PUT"],
    #         },
    #         {
    #             "path": "/products/<int:product_id>",
    #             "description": "Delete a Product based on the id specified in the path",
    #             "methods": ["DELETE"],
    #         },
    #         {
    #             "path": "/products/<int:product_id>/change_availability",
    #             "description": "Change the availability of a Product based on the id specified in the path",
    #             "methods": ["POST"],
    #         },
    #     ],
    # }
    return app.send_static_file("index.html")

# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Product",
    {
        "name": fields.String(required=True, description="The name of the Product"),
        "description": fields.String(
            required=True,
            description="The description of Product",
        ),
        "price": fields.Float(
            required=True,
            description="The price of Product",
        ),
        "available": fields.Boolean(
            required=True, description="Is the Product available for purchase?"
        ),
        "image_url": fields.String(
            required=True,
            description="The image url of Product",
        ),
        # pylint: disable=protected-access
        "category": fields.String(
            enum=Category._member_names_, 
            description="he category of Product (e.g., ELECTRONICS, FOOD, etc.)"
        ),
    },
)

product_model = api.inherit(
    "ProductModel",
    create_model,
    {
        "id": fields.String(
            readOnly=True, description="The unique id assigned internally by service"
        ),
    },
)

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument(
    "name", type=str, location="args", required=False, help="List Products by name"
)
product_args.add_argument(
    "category", type=str, location="args", required=False, help="List Products by category"
)
product_args.add_argument(
    "available",
    type=inputs.boolean,
    location="args",
    required=False,
    help="List Products by availability",
)
######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

######################################################################
#  PATH: /products/{id}
######################################################################
@api.route("/products/<product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /product{id} - Returns a Product with the id
    PUT /product{id} - Update a Product with the id
    DELETE /product{id} -  Deletes a Product with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("get_products")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a single Product

        This endpoint will return a Product based on it's id
        """
        app.logger.info("Request to Retrieve a product with id [%s]", product_id)
        product = Product.find(product_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc("update_products")
    @api.response(404, "Product not found")
    @api.response(400, "The posted Product data was not valid")
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Update a Product

        This endpoint will update a Product based the body that is posted
        """
        app.logger.info("Request to Update a product with id [%s]", product_id)
        product = Product.find(product_id)
        if not product:
            abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        product.deserialize(data)
        product.id = product_id
        product.update()
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("delete_products")
    @api.response(204, "Product deleted")
    def delete(self, product_id):
        """
        Delete a Product

        This endpoint will delete a Product based the id specified in the path
        """
        app.logger.info("Request to Delete a product with id [%s]", product_id)
        product = Product.find(product_id)
        if product:
            product.delete()
            app.logger.info("Product with id [%s] was deleted", product_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products
######################################################################
@api.route("/products", strict_slashes=False)
class ProductCollection(Resource):
    """Handles all interactions with collections of Products"""

    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS
    # ------------------------------------------------------------------
    @api.doc("list_products")
    @api.expect(product_args)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns all of the Products"""
        app.logger.info("Request to list Products...")
        products = []
        args = product_args.parse_args()
        if args["category"]:
            app.logger.info("Filtering by category: %s", args["category"])
            products = Product.find_by_category(args["category"])
        elif args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            products = Product.find_by_name(args["name"])
        elif args["available"] is not None:
            app.logger.info("Filtering by availability: %s", args["available"])
            products = Product.find_by_availability(args["available"])
        else:
            app.logger.info("Returning unfiltered list.")
            products = Product.all()

        results = [product.serialize() for product in products]
        app.logger.info("[%s] Products returned", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT
    # ------------------------------------------------------------------
    @api.doc("create_products")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(product_model, code=201)
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based the data in the body that is posted
        """
        app.logger.info("Request to Create a Product")
        product = Product()
        app.logger.debug("Payload = %s", api.payload)
        product.deserialize(api.payload)
        product.create()
        app.logger.info("Product with new id [%s] created!", product.id)
        location_url = api.url_for(ProductResource, product_id=product.id, _external=True)
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
#  PATH: /products/{id}/change_availability
######################################################################
@api.route("/products/<product_id>/change_availability")
@api.param("product_id", "The Product identifier")
class PurchaseResource(Resource):
    """Change availability actions on a Product"""

    @api.doc("change_availability")
    @api.response(404, "Product not found")
    def put(self, product_id):
        """
        Purchase a Product

        This endpoint will purchase a Product and make it unavailable
        """
        app.logger.info(
            "Request to change availability for product with id: %s", product_id
        )
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        new_availability = not product.available
        product.available = new_availability
        db.session.commit()
        message = {"message": f"Product availability changed to {new_availability}"}
        message = {**message, **product.serialize()}

        app.logger.info("Product availability changed for ID [%s].", product_id)

        return jsonify(message), status.HTTP_200_OK
        
        product.available = False
        product.update()
        app.logger.info("Product with id [%s] has been purchased!", product.id)
        return product.serialize(), status.HTTP_200_OK


# ######################################################################
# # LIST ALL PRODUCTS
# ######################################################################
# @app.route("/products", methods=["GET"])
# def list_products():
#     """Returns all of the Products"""
#     app.logger.info("Request for product list")
#     category = request.args.get("category")
#     name = request.args.get("name")
#     available = request.args.get("available")
#     products = Product.all()

#     if category:
#         products_category = Product.find_by_category(category)
#         products = [product for product in products if product in products_category]
#     if name:
#         products_name = Product.find_by_name(name)
#         products = [product for product in products if product in products_name]
#     if available:
#         products_available = Product.find_by_availability(available)
#         products = [product for product in products if product in products_available]

#     results = [product.serialize() for product in products]
#     app.logger.info("Returning %d products", len(results))
#     return jsonify(results), status.HTTP_200_OK


# ######################################################################
# # ADD A NEW PRODUCT
# ######################################################################
# @app.route("/products", methods=["POST"])
# def create_products():
#     """
#     Creates a Product
#     This endpoint will create a Product based the data in the body that is posted
#     """
#     app.logger.info("Request to create a product")
#     check_content_type("application/json")
#     product = Product()
#     product.deserialize(request.get_json())
#     product.create()
#     message = product.serialize()
#     location_url = url_for("read_products", product_id=product.id, _external=True)
#     app.logger.info("Product with ID [%s] created.", product.id)
#     return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

#     # try:
#     #     product.deserialize(request.get_json())
#     #     product.create()
#     #     message = product.serialize()
#     #     location_url = url_for("read_products", product_id=product.id, _external=True)
#     #     app.logger.info("Product with ID [%s] created.", product.id)
#     #     return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
#     # except sqlalchemy.exc.PendingRollbackError as rollback_error:
#     #     # Rollback the session in case of error
#     #     db.session.rollback()
#     #     print("rollback")
#     #     app.logger.error("Error creating product: %s", str(rollback_error))
#     #     return jsonify({"error": "Error creating product"}), status.HTTP_400_BAD_REQUEST


######################################################################
# ADD MULTIPLE NEW PRODUCT
######################################################################
@app.route("/products/collect", methods=["POST"])
def create_collect_products():
    """
    Creates multiple Products
    This endpoint will create multiple Products based the data in the body that is posted
    """
    app.logger.info("Request to create multiple products")
    check_content_type("application/json")
    products_data = request.get_json()
    products = Product.create_multiple_products(products_data)
    message = []
    for product in products:
        app.logger.info("Product with ID [%s] created.", product.id)
        message.append(product.serialize())
    return jsonify(message), status.HTTP_201_CREATED


# ######################################################################
# # UPDATE A PRODUCT
# ######################################################################
# @app.route("/products/<int:product_id>", methods=["PUT"])
# def update_product(product_id):
#     """
#     Update a Product
#     This endpoint will update a existing Product based the data in the body that is posted
#     or return 404 there is no product with id provided in payload
#     """

#     app.logger.info("Request to update a product")
#     check_content_type("application/json")

#     product: Product = Product.find(product_id)
#     if not product:
#         app.logger.info("Invalid product id: %s", product_id)
#         abort(
#             status.HTTP_404_NOT_FOUND, f"There is no exist product with id {product_id}"
#         )
#     product.deserialize(request.get_json())
#     product.update()
#     message = product.serialize()

#     return jsonify(message), status.HTTP_200_OK


# ######################################################################
# # DELETE A PRODUCT
# ######################################################################
# @app.route("/products/<int:product_id>", methods=["DELETE"])
# def delete_products(product_id):
#     """
#     Delete a Product
#     This endpoint will delete a Product based the id specified in the path
#     """
#     app.logger.info("Request to delete product with id: %s", product_id)
#     product = Product.find(product_id)
#     if product:
#         product.delete()

#     app.logger.info("Product with ID [%s] delete complete.", product_id)
#     return "", status.HTTP_204_NO_CONTENT


# ######################################################################
# # READ A PRODUCT
# ######################################################################
# @app.route("/products/<int:product_id>", methods=["GET"])
# def read_products(product_id):
#     """
#     Read a Product
#     This endpoint will Read a Product for detail based the id specified in the path
#     """
#     app.logger.info("Request to read product with id: %s", product_id)
#     product = Product.find(product_id)
#     if not product:
#         abort(
#             status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
#         )

#     app.logger.info("Returning product with ID [%s].", product_id)
#     return jsonify(product.serialize()), status.HTTP_200_OK


# ######################################################################
# # ACTION TO CHANGE A PRODUCT'S AVAILABILITY
# ######################################################################
# @app.route("/products/<int:product_id>/change_availability", methods=["PUT"])
# def change_product_availability(product_id):
#     """
#     Change Product Availability
#     This endpoint will change the availability of a Product based on the id specified in the path.
#     """
#     app.logger.info(
#         "Request to change availability for product with id: %s", product_id
#     )
#     product = Product.find(product_id)
#     if not product:
#         abort(
#             status.HTTP_404_NOT_FOUND,
#             f"Product with id '{product_id}' was not found.",
#         )

#     new_availability = not product.available
#     product.available = new_availability
#     db.session.commit()
#     message = {"message": f"Product availability changed to {new_availability}"}
#     message = {**message, **product.serialize()}

#     app.logger.info("Product availability changed for ID [%s].", product_id)

#     return jsonify(message), status.HTTP_200_OK


######################################################################
# get product categories
######################################################################
@app.route("/categories", methods=["GET"])
def get_categories():
    """Endpoint to get product categories"""
    categories = [category.name for category in Category]
    return jsonify(categories)


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
