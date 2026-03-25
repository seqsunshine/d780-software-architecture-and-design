Retail Checkout Microservices in Python <br>
This project is a lightweight microservices-based retail checkout system built in Python using the standard library HTTP server modules. It separates core e-commerce functions into independent services for inventory, payments, cart management, and checkout orchestration. The goal of the project is to demonstrate service decomposition, inter-service communication, and basic transaction handling without relying on heavyweight web frameworks. <br>
Project Overview <br>
The application is split into four services: <br>
-Inventory Service handles stock updates and stock lookups for items. <br>
-Payment Service processes payment charges and refunds. <br>
-Cart Service manages cart contents for individual users. <br>
-Orchestrator Service coordinates the checkout workflow by validating inventory, decrementing stock, charging payment, and restoring inventory if payment fails. <br>
This design reflects a simple microservices architecture where each service owns a focused responsibility and communicates through HTTP requests. The project highlights how a monolithic checkout process can be separated into smaller services while still supporting a complete purchase flow. <br>
What This Project Demonstrates <br>
This project was built to show practical understanding of: <br>
-Microservices architecture <br>
-REST-style endpoint design <br>
-HTTP request handling in Python <br>
-Service orchestration <br>
-Basic fault handling and rollback logic <br>
-JSON-based communication between services <br>
One of the more important pieces is the orchestrator, which acts as the coordinator for checkout. It checks current inventory, reduces stock when enough inventory exists, submits the payment request, and restores stock if the payment step fails. That rollback behavior helps simulate a more reliable distributed transaction flow in a simple educational project. <br>
Tech Stack <br>
-Language: Python 3.10 <br>
-Libraries: Python standard library only <br>
--http.server <br>
--urllib <br>
--json <br>
--uuid <br>
--os <br>
-Testing/usage: cURL for endpoint interaction and manual testing
