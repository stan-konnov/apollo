### On Alpaca Extended Hours Trading

* To indicate an order is eligible for extended hours trading,
you need to supply a boolean parameter named `extended_hours` to your order request.
By setting this parameter to true, the order is will be eligible to execute in the pre-market or after-hours.

* Only limit day orders will be accepted as extended hours eligible.
All other order types and TIFs will be rejected with an error.
You must adhere to these settings in order to participate in extended hours:

* The order type must be set to `limit` (with a limit price).
Any other type of orders will be rejected with an error.
Time-in-force must be set to be `day`. Any other time_in_force will be rejected with an error.