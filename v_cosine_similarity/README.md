# v_cosine_similarity Vertica UDX

This document provides instructions on how to install and use the `v_cosine_similarity` User-Defined Extension (UDX) in Vertica. The `v_cosine_similarity` function computes the cosine similarity between two vectors, which must be provided as JSON array strings. It returns a float value representing the similarity, ranging from -1.0 to 1.0.

## Prerequisites

*   A running Vertica database.
*   The `v_cosine_similarity.py` script must be accessible from the Vertica server nodes.
*   Sufficient database privileges to create libraries and functions.

This UDX uses the standard Python `json` and `math` libraries, which are included with Python, so no external package installation is required.

## Installation

1.  **Copy the Script:**
    Place the `v_cosine_similarity.py` script in a directory accessible by the `dbadmin` user on all Vertica nodes. For this example, we'll assume it's located at `/home/dbadmin/vertica_pyudx/v_cosine_similarity/v_cosine_similarity.py`.

2.  **Create the Library and Function:**
    Run the following SQL commands in `vsql` or your preferred Vertica client. This script creates the library pointing to the Python file and then defines the `v_cosine_similarity` function from that library.

    ```sql
    -- Create a library for the v_cosine_similarity Python UDX.
    -- IMPORTANT: Update the path to reflect the actual location of 'v_cosine_similarity.py' on your Vertica nodes.
    CREATE OR REPLACE LIBRARY VerticaExtPy_V_CosineSimilarity AS '/home/dbadmin/vertica_pyudx/v_cosine_similarity/v_cosine_similarity.py' LANGUAGE 'Python';

    -- Create the scalar function, linking it to the factory in the library.
    CREATE OR REPLACE FUNCTION public.v_cosine_similarity AS LANGUAGE 'Python' NAME 'v_cosine_similarity_factory' LIBRARY VerticaExtPy_V_CosineSimilarity FENCED;
    ```
    
    You can also execute the provided `install.sql` file after ensuring the path within the file is correct for your environment.

3.  **Grant Privileges (Optional):**
    To allow other users to execute the function, grant them the necessary privileges:

    ```sql
    GRANT EXECUTE ON FUNCTION public.v_cosine_similarity TO PUBLIC;
    ```

## Usage

The `v_cosine_similarity` function takes two string arguments, each representing a numerical vector in JSON array format, and returns their cosine similarity as a float.

**Syntax:**
`v_cosine_similarity(vector1_json, vector2_json)`

*   `vector1_json` (VARCHAR): A JSON string representing the first vector (e.g., `'[1, 2, 3]'`).
*   `vector2_json` (VARCHAR): A JSON string representing the second vector (e.g., `'[4, 5, 6]'`).

**Example:**

```sql
-- Example: Calculating cosine similarity between two simple vectors
SELECT v_cosine_similarity('[1, 2, 3]', '[1, 2, 3]');
```
Output:
```
 v_cosine_similarity
---------------------
                   1
(1 row)
```

```sql
SELECT v_cosine_similarity('[1, 2, 3]', '[4, 5, 6]');
```
Output:
```
 v_cosine_similarity
---------------------
  0.9746318461970762
(1 row)
```


**Example with table data:**
```sql
-- Example: Calculating similarity from vector data in a table
CREATE TABLE document_vectors (id INT, doc_name VARCHAR(50), vector_json VARCHAR(200));
INSERT INTO document_vectors VALUES (1, 'doc_A', '[0.1, 0.5, 0.9]');
INSERT INTO document_vectors VALUES (2, 'doc_B', '[0.12, 0.45, 0.85]');
INSERT INTO document_vectors VALUES (3, 'doc_C', '[0.8, 0.2, 0.1]');
COMMIT;

-- Compare doc_A with all other documents
SELECT
    d1.doc_name AS doc1,
    d2.doc_name AS doc2,
    v_cosine_similarity(d1.vector_json, d2.vector_json) AS similarity
FROM document_vectors d1, document_vectors d2
WHERE d1.id = 1 AND d1.id <> d2.id;
```
Output:
```
 doc1  | doc2  |    similarity
-------+-------+--------------------
 doc_A | doc_B | 0.9986424361546311
 doc_A | doc_C | 0.3542151327329037
(2 rows)
```

## Uninstallation

To remove the function and library from your database, run the `uninstall.sql` script or execute the following command:

```sql
DROP LIBRARY IF EXISTS VerticaExtPy_V_CosineSimilarity CASCADE;
```
This command removes the library and any functions that depend on it.
