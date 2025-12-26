# Installation Guide for v_sentiment Vertica UDX

This document outlines the steps to install and use the `v_sentiment` User-Defined Extension (UDX) in Vertica. This UDX allows you to perform sentiment analysis on text data using IDOL Eduction Server within Vertica using a custom Python scalar function that communicates with an external eduction service.

## Prerequisites

*   A running Vertica database.
*   An accessible eduction service for sentiment analysis.
*   Python's `requests` package must be available in the Vertica Python environment. To install it, you can use the following commands:

```bash
cd /home/dbadmin
/opt/vertica/sbin/python3 -m venv vertica_pyudx
source vertica_pyudx/bin/activate
pip install requests
```

This will create a Python virtual environment and install the `requests` library. The `install.sql` script assumes that the new packages are in `/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages`.

*   Sufficient privileges to create functions and libraries in Vertica.

## Installation Steps

1.  **Create the Library:**

First, you need to create a library in Vertica that points to the location of your Python script (`v_sentiment.py`).  Make sure the file is accessible by the Vertica server.

```sql
CREATE OR REPLACE LIBRARY VerticaExtPy_V_Sentiment AS 
'/home/dbadmin/vertica_pyudx/v_sentiment/v_sentiment.py' 
depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' LANGUAGE 'Python';
```

*   Replace `/home/dbadmin/vertica_pyudx/v_sentiment/v_sentiment.py` with the actual path to your `v_sentiment.py` file on the Vertica server.
*   Replace `/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*` with the actual path to your site-packages directory, including the trailing `/*` to ensure all packages are loaded.

2.  **Create the Function:**

Now, create the scalar function in Vertica, associating it with the library you just created.

```sql
CREATE OR REPLACE FUNCTION public.v_sentiment AS LANGUAGE 'Python' NAME 'v_sentiment_factory' LIBRARY VerticaExtPy_V_Sentiment fenced;
```

3.  **Grant Usage Privileges (if necessary):**

If other users need to use this function, grant them usage privileges on the library and execute privileges on the function:

```sql
GRANT USAGE ON LIBRARY VerticaExtPy_V_Sentiment TO PUBLIC; -- Or to specific users/roles
GRANT EXECUTE ON FUNCTION public.v_sentiment TO PUBLIC; -- Or to specific users/roles
```

## Usage

Now you can use the `v_sentiment` function in your Vertica SQL queries.

**Syntax:**

`v_sentiment(eduction_service_url, text_to_analyze)`

*   `eduction_service_url`: The URL of the eduction service that will perform the sentiment analysis.
*   `text_to_analyze`: The text data you want to analyze.

The function will return one of the following string values:
*   `positive`
*   `negative`
*   `mixed`
*   `neutral`

**Example:**

```sql
select v_sentiment('http://192.168.100.12:13000', 'too bad the movie was so boring and dull');
```

## Notes
*   This UDX returns a string (`VARCHAR(100)`).
*   Ensure that the Python script (`v_sentiment.py`) and its dependencies are compatible with the Vertica Python environment.
*   The eduction service must be reachable from the Vertica nodes.