Configuration
=============

To run the agent-based system correctly, you must provide configuration parameters for accessing external APIs and databases.

These parameters must be placed in a file named `config.yaml` located at the **root of the repository**.

The `config.yaml` file is used both at runtime and during documentation generation (e.g., on ReadTheDocs), and it must contain the following keys:

.. code-block:: yaml

    project: "your-project-code"
    location: "your-server-location"
    INFLUXDB_URL: "http://dummy-url"
    INFLUXDB_TOKEN: "your-influxdb-token"
    INFLUXDB_ORG: "your-influxdb-org"
    INFLUXDB_BUCKET: "your-influxdb-bucket"
    ELS_API_KEY: "your-elsevier-api-key"

The configuration loader prioritizes environment variables (if set), and falls back to this file if any variable is missing.

.. note::
   If the `config.yaml` file is missing, the system may raise a ``FileNotFoundError`` or ``KeyError``, especially during local tests or documentation builds.

Make sure to include this file in your development setup and document it for other users or team members.