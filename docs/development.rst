===========
Development
===========

Crabpy is still in development, but the general API is stable and we are already 
using it in production.

We try to cover as much code as we can with tests. You can run them using pytest.
Use `coverage` for coverage results.

.. code-block:: bash
    # No coverage
    $ pytest tests
    # Coverage
    $ coverage --source crabpy crabpy -m pytest tests
.. 
