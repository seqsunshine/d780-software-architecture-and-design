Name: Sequoia Hancock
Student ID: 010184738
Python Version: 3.10

Description of each function:

Inventory Function:
This function includes update_stock, which will increase or decrease the stock for an item.
It also includes get_stock which will return the current stock for the item requested. 

Payment Function:
This function includes charge_payment which will capture a payment for the requested payment form.
The refund_payment function is also included, and will refund a previous charge in accordance to the previously
selected payment form.

Cart Function:
This function includes the add_item function, which adds an item to the current user's cart.
It also includes get_cart which will return a user's current cart. Additionally, it includes clear_cart which will
empty the current user's cart.

Orchestrator:
This will pull all the different functions together to use the checkout function. This will check stock, decrement
inventory, charge payment, and give the user a confirmation message. If the payment fails, it will restore the stock
to inventory.

Steps to run each function:

1) Start services in separate terminals
- Terminal 1: Inventory
python inventory_service.py 5001
- Terminal 2: Payment
python payment_service.py 5002
- Terminal 3: Orchestrator
python orchestrator_service.py 5000
- Terminal 4: Cart
python cart_service.py 5003

2) Run update stock
curl -X PUT http://localhost:5001/inventory/Laptop \
    -H "Content-Type: application/json" \
    -d '{ "quantity": 5 }'
3) Run stock check
curl -X GET http://localhost:5001/inventory/Laptop
4) Run payment
curl -X POST http://localhost:5000/checkout \
    -H "Content-Type: application/json" \
    -d '{ "item": "Laptop", "quantity": 2, "method": "credit_card", "amount": 2000}'