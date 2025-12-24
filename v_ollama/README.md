# Installation Guide for v_ollama_embedding Vertica UDX

This document outlines the steps to install and use the `v_ollama_embedding` User-Defined Extension (UDX) in Vertica. This UDX allows you to generate vector within Vertica using a custom Python scalar function.

## Prerequisites

*   A running Vertica database.
*   To avoid problems when loading and executing your UDxs, develop your UDxs using the same version of Python that Vertica uses, we will use Vertica's python to download additional python package that we needed :

    ```bash
    cd /home/dbadmin
    /opt/vertica/sbin/python3 -m venv vertica_pyudx
    source vertica_pyudx/bin/activate
    pip install ollama
    ```
    and now we will have site-packages that what we need , check your path's content, Python version will depend on your Vertica version, I'm using Vertica 25.3.0 and it bundles with Python 3.13 :
    
    /home/dbadmin/vertica_pyudx/lib/python3.13/site-packages

*   Sufficient privileges to create functions and libraries in Vertica.

## Installation Steps

1.  **Create the Library:**

    First, you need to create a library in Vertica that points to the location of your Python script (`v_ollama.py`).  Make sure the file is accessible by the Vertica server.  If it's not on the server, you'll need to copy it there.

    ```sql
    CREATE OR REPLACE LIBRARY VerticaExtPy_V_Ollama_Embedding AS 
    '/home/dbadmin/vertica_pyudx/v_ollama/v_ollama.py' 
    depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' LANGUAGE 'Python';
    ```

    *   Replace `/home/dbadmin/vertica_pyudx/v_generate_series/v_ollama.py` with the actual path to your `v_ollama.py` file on the Vertica server.

    *   Replace `/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*` with 
    the actual path to your site-packages directory config in previous step.

2.  **Create the Function:**

    Now, create the scalar function in Vertica, associating it with the library you just created.

    ```sql
    CREATE OR REPLACE FUNCTION public.v_ollama_embedding AS LANGUAGE 'Python' NAME 'v_ollama_embedding_factory' LIBRARY VerticaExtPy_V_Ollama_Embedding fenced;
    ```

3.  **Grant Usage Privileges (if necessary):**

    If other users need to use this function, grant them usage privileges on the library:

    ```sql
    GRANT USAGE ON LIBRARY VerticaExtPy_V_Ollama_Embedding TO PUBLIC; -- Or to specific users/roles
    ```

    ```sql
    GRANT EXECUTE ON FUNCTION public.v_ollama_embedding TO PUBLIC; -- Or to specific users/roles
    ```

## Usage

Now you can use the `v_ollama_embedding` function in your Vertica SQL queries.
** Text only, no image or others **

**Syntax:**

    v_ollama_embedding(host, model, dimension, text)

    1. host: 
        The URL of Ollama, for example : http://localhost:11434
    2. model: 
        The embedding model that you want to use, must be install on Ollama first, for example you may using embeddinggemma or qwen3-embedding or other model that you may choose
    3. dimension: 
        the dimension of vector, depend on the embedding model, the max size is 4096, if this number bigger than model provide, will using the biggest dimension that mdoel provide

    ```sql
    select v_ollama_embedding('http://192.168.100.12:11434', 'qwen3-embedding', 4096,  'Hello World')
    select v_ollama_embedding('http://192.168.100.12:11434', 'embeddinggemma', 768,  'Hello World')
    ```

## Notes
*    1. This UDX returns an array of float.
*    2. Ensure that the Python script (v_ollama.py) is compatible with the Vertica Python environment.
*    3. After you have vector in your data, you may reference /opt/vertica/packages/VectorOps, Vertica provide vector distince caculate function.

