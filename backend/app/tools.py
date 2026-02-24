import json
import re

from .database import (
    find_customers_by_last_name,
    find_customers_by_name,
    find_order_by_id,
    find_orders_by_customer_id,
    find_product_by_id,
    find_products_by_name,
)
from .utils import json_serializer, validate_id, validate_name, validate_product_search


# Tools available to Claude
def get_order(order_id: str) -> str:
    if not validate_id(order_id):
        return json.dumps({"status": "error", "message": "Invalid Order ID provided."})

    customer_order = find_order_by_id(order_id=order_id)
    if not customer_order:
        return json.dumps(
            {
                "status": "no_match",
                "message": f"No order data available for Order ID: '{order_id}'.",
            }
        )
    return json.dumps({"status": "success", "data": customer_order}, default=json_serializer)


def get_orders(last_name: str, first_name: str | None = None) -> str:

    # So your full case list is:
    #     No last name provided — return error
    #     Last name matches nobody — return no match error
    #     Last name matches, no first name provided, one customer found — proceed to order lookup
    #     Last name matches, no first name provided, multiple customers found — ask for clarification
    #     Last name matches, first name provided, one fuzzy match — proceed
    #     Last name matches, first name provided, multiple fuzzy matches — ask for clarification
    #     Last name matches, first name provided, no first name match — return no match error

    if not last_name:
        return json.dumps(
            {
                "status": "error",
                "message": "Last name is required.",
            }
        )

    if not validate_name(last_name):
        return json.dumps({"status": "error", "message": "Invalid name provided."})

    matching_customers = find_customers_by_last_name(last_name=last_name)
    if not matching_customers:
        return json.dumps(
            {
                "status": "no_match",
                "message": f"No customers found for the last name: '{last_name}'.",
            }
        )

    elif len(matching_customers) == 1:
        customer_id = matching_customers[0].get("id")
        customer_orders = find_orders_by_customer_id(customer_id=customer_id)

        return json.dumps({"status": "success", "data": customer_orders}, default=json_serializer)

    elif len(matching_customers) > 1:
        if not first_name:
            return json.dumps(
                {
                    "status": "multiple_matches",
                    "message": f"Multiple customers found with the last name: '{last_name}'. Please provide a first name to further narrow the results.",
                }
            )

        if not validate_name(first_name):
            return json.dumps({"status": "error", "message": "Invalid name provided."})

        matching_customers = find_customers_by_name(last_name=last_name, first_name=first_name)
        if not matching_customers:
            return json.dumps(
                {
                    "status": "no_match",
                    "message": f"No customers found for the last name: '{last_name}' and first name: '{first_name}'.",
                }
            )

        elif len(matching_customers) == 1:
            customer_id = matching_customers[0].get("id")
            customer_orders = find_orders_by_customer_id(customer_id=customer_id)

            return json.dumps(
                {"status": "success", "data": customer_orders}, default=json_serializer
            )

        elif len(matching_customers) > 1:
            return json.dumps(
                {
                    "status": "multiple_matches",
                    "message": f"Multiple customers found with the last name: '{last_name}' and first name: '{first_name}'. Please provide your order ID to proceed.",
                }
            )

    # Should never reach here, but just in case
    return json.dumps({"status": "error", "message": "An unexpected error occurred."})


def get_product_by_id(product_id: str) -> str:
    if not validate_id(product_id):
        return json.dumps({"status": "error", "message": "Invalid Product ID provided."})

    product = find_product_by_id(product_id=product_id)
    if not product:
        return json.dumps(
            {
                "status": "no_match",
                "message": f"No product data available for product ID: '{product_id}'.",
            }
        )

    return json.dumps({"status": "success", "data": product}, default=json_serializer)


def get_product_by_name(product_name: str) -> str:

    if not product_name:
        return json.dumps(
            {
                "status": "error",
                "message": "Product name is required.",
            }
        )

    if not validate_product_search(product_name):
        return json.dumps(
            {
                "status": "error",
                "message": "Invalid Product name provided.",
            }
        )

    search_words = product_name.split()
    matching_products = find_products_by_name(search_words=search_words)
    if not matching_products:
        return json.dumps(
            {
                "status": "no_match",
                "message": f"No products found for the provided name: '{product_name}'.",
            }
        )

    elif len(matching_products) == 1:
        return json.dumps(
            {"status": "success", "data": matching_products[0]}, default=json_serializer
        )

    elif len(matching_products) > 1:
        return json.dumps(
            {
                "status": "multiple_matches",
                "message": f"Multiple products found for '{product_name}'.",
                "matches": [p["ProductName"] for p in matching_products],
            }
        )

    # Should never reach here, but just in case
    return json.dumps({"status": "error", "message": "An unexpected error occurred."})


# Schema list sent to Claude to describe the tools
tools = [
    {
        "name": "get_order",
        "description": "Gets a single order for a given order_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order_id for which to look up the order",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_orders",
        "description": "Gets all orders for a given customer_name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "last_name": {
                    "type": "string",
                    "description": "Customer's last name, case insensitive.",
                },
                "first_name": {
                    "type": "string",
                    "description": "Customer's first name, optional. Provide if you have it to narrow results.",
                },
            },
            "required": ["last_name"],
        },
    },
    {
        "name": "get_product_by_id",
        "description": "Gets product information for a given product_id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The product_id for which to look up the product",
                }
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "get_product_by_name",
        "description": "Gets product information for a given product_name.",
        "input_schema": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Product name, case insensitive, fuzzy search.",
                }
            },
            "required": ["product_name"],
        },
    },
]


def process_tool_call(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_order":
        return get_order(tool_input["order_id"])
    elif tool_name == "get_orders":
        return get_orders(tool_input.get("last_name"), tool_input.get("first_name"))
    elif tool_name == "get_product_by_id":
        return get_product_by_id(tool_input["product_id"])
    elif tool_name == "get_product_by_name":
        return get_product_by_name(tool_input["product_name"])
    return "Unknown tool"
