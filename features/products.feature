Feature: The Products service back-end
    As a Products Manager
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name    | description | price | available | image_url  | category    |
        | iPhone 15  | Best iphone for now  | 999   | True      | sample.url | ELECTRONICS |
        | iPhone 16  | Best iphone for now  | 999   | False      | sample.url | ELECTRONICS |
        | milk    | Oat Milk    | 10    | True      | sample.url | FOOD        |
        | egg     | Organic Egg | 1     | True      | sample.url | FOOD        |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product REST API Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Ball"
    And I select "SPORTS" in the "Category" dropdown
    And I set the "Description" to "Basketball"
    And I set the "Price" to "100"
    And I select "True" in the "Available" dropdown
    And I set the "image_url" to "sample.url"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Ball" in the "Name" field
    And I should see "SPORTS" in the "Category" field
    And I should see "Basketball" in the "Description" field
    And I should see "100" in the "Price" field
    And I should see "True" in the "Available" dropdown
    And I should see "sample.url" in the "image_url" field


Scenario: Delete a Product
    When I visit the "Home Page"
    # get Available=Flase produect
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "iPhone 16" in the "Name" field
    And I should see "ELECTRONICS" in the "Category" field
    And I should see "Best iphone for now" in the "Description" field
    And I should see "False" in the "Available" dropdown

    # copy ID and clear data
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty

    # paste ID and delete produect
    When I paste the "Id" field
    And I press the "Delete" button
    Then I should see the message "Product has been Deleted!"
    When I press the "Retrieve" button
    Then I should see the message "not found"

Scenario: Update a Product
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"

    # copy ID and clear data
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty

    # paste ID and Retrieve produect
    When I paste the "Id" field
    When I press the "Retrieve" button

    # update product
    And I set the "Name" to "Ball"
    And I select "SPORTS" in the "Category" dropdown
    And I set the "Description" to "Basketball"
    And I set the "Price" to "100"
    And I select "True" in the "Available" dropdown
    And I set the "image_url" to "sample.url"
    And I press the "Update" button
    Then I should see the message "Success"


    When I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty

    # check the updated product
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Ball" in the "Name" field
    And I should see "SPORTS" in the "Category" field
    And I should see "Basketball" in the "Description" field
    And I should see "100" in the "Price" field
    And I should see "True" in the "Available" dropdown
    And I should see "sample.url" in the "image_url" field

Scenario: List all Products
    When I visit the "Home Page"
    And I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "iPhone 15" in the results
    And I should see "iPhone 16" in the results
    And I should see "milk" in the results
    And I should see "egg" in the results

Scenario: Read a Product by ID
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "iPhone 15" in the "name" field
    And I should see "Best iphone for now" in the "description" field
    And I should see "999" in the "price" field
    And I should see "True" in the "available" dropdown
    And I should see "sample.url" in the "image_url" field
    And I should see "ELECTRONICS" in the "category" field

Scenario: Query a Product by Name
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Name" to "iPhone 15"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "iPhone 15" in the results
    And I should see "999" in the results
    And I should see "true" in the results
    And I should see "ELECTRONICS" in the results
    And I should see "Best iphone for now" in the results
    And I should see "sample.url" in the results

Scenario: Query a Product by Category
    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "FOOD" in the "Category" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "milk" in the results
    And I should see "egg" in the results

Scenario: Query a Product by Available
    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "iPhone 16" in the results

Scenario: Action Change the Availability of a Product
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Category" field should be empty
    And the "Description" field should be empty
    And the "Price" field should be empty
    And the "image_url" field should be empty
    When I paste the "Id" field
    And I press the "Change Availability" button
    Then I should see the message "Product availability changed to False"
    And I should see "iPhone 15" in the "name" field
    And I should see "Best iphone for now" in the "description" field
    And I should see "999" in the "price" field
    And I should see "False" in the "available" dropdown
    And I should see "sample.url" in the "image_url" field
    And I should see "ELECTRONICS" in the "category" field