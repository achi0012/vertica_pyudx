# Installation Guide for v_generate_series Vertica UDX

This document outlines the steps to install and use the `v_generate_series` User-Defined Extension (UDX) in Vertica. This UDX allows you to generate time series data within Vertica using a custom Python scalar function.

## Prerequisites

*   A running Vertica database.
*   To avoid problems when loading and executing your UDxs, develop your UDxs using the same version of Python that Vertica uses, we will use Vertica's python to download additional python package that we needed :

    ```bash
    cd /home/dbadmin
    /opt/vertica/sbin/python3 -m venv vertica_pyudx
    source vertica_pyudx/bin/activate
    pip install python-dateutil
    ```
    and now we will have site-packages that what we need , check your path's content, Python version will depend on your Vertica version, I'm using Vertica 25.3.0 and it bundles with Python 3.13 :
    
    /home/dbadmin/vertica_pyudx/lib/python3.13/site-packages

*   Sufficient privileges to create functions and libraries in Vertica.

## Installation Steps

1.  **Create the Library:**

    First, you need to create a library in Vertica that points to the location of your Python script (`v_generate_series.py`).  Make sure the file is accessible by the Vertica server.  If it's not on the server, you'll need to copy it there.

    ```sql
    CREATE OR REPLACE LIBRARY public.VerticaExtPy_V_Generate_Series AS  '/home/dbadmin/vertica_pyudx/v_generate_series/v_generate_series.py' depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' 
    LANGUAGE 'Python';
    ```

    *   Replace `/home/dbadmin/vertica_pyudx/v_generate_series/v_generate_series.py` with the actual path to your `v_generate_series.py` file on the Vertica server.

    *   Replace `/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*` with 
    the actual path to your site-packages directory config in previous step.

2.  **Create the Function:**

    Now, create the scalar function in Vertica, associating it with the library you just created.

    ```sql
    CREATE FUNCTION IF NOT EXISTS public.v_generate_series AS LANGUAGE 'Python' NAME 'v_generate_series_factory' LIBRARY VerticaExtPy_V_Generate_Series fenced;
    ```

3.  **Grant Usage Privileges (if necessary):**

    If other users need to use this function, grant them usage privileges on the library:

    ```sql
    GRANT USAGE ON LIBRARY VerticaExtPy_V_Generate_Series TO PUBLIC; -- Or to specific users/roles
    ```

    ```sql
    GRANT EXECUTE ON FUNCTION public.v_generate_series TO PUBLIC; -- Or to specific users/roles
    ```

## Usage

Now you can use the `v_generate_series` function in your Vertica SQL queries.

**Syntax:**

    v_generate_series(start_time, end_time, interval)

    1. tart_time: 
        The starting timestamp for the series (VARCHAR). 
        Format: 'YYYY-MM-DD HH:MI:SS'
    2. end_time: 
        The ending timestamp for the series (VARCHAR). 
        Format: 'YYYY-MM-DD HH:MI:SS'
    3. interval: 
        The interval between timestamps (VARCHAR). Valid values:
        S: Seconds
        MI: Minutes
        H: Hours
        D: Days
        W: Weeks
        M: Months
        Q: Quarters
        Y: Years

    ```sql
    SELECT v_generate_series('2023-01-01 00:00:00', '2023-01-01 01:00:00', 'D');
    SELECT v_generate_series('2023-01-01 00:00:00', '2023-01-01 01:00:00', 'M');
    ```

## Notes
*    1. This UDX returns an array of timestamps. You might need to unnest the array for further processing or analysis.
*    2. Ensure that the Python script (v_generate_series.py) is compatible with the Vertica Python environment.
*    3. Due to Vertica ARRAY type's limitation, this function can only return **64000** items, for seconds, minutes usage it might not enough, will continue update if Vertica can support it.

