# v_hash Vertica UDX

This document provides instructions on how to install and use the `v_hash` User-Defined Extension (UDX) in Vertica. The `v_hash` function computes a SHA256 hash of a given string and returns it as a fixed-length string.

## Prerequisites

*   A running Vertica database.
*   The `v_hash.py` script must be accessible from the Vertica server nodes.
*   Sufficient database privileges to create libraries and functions.

This UDX uses the standard Python `hashlib` library, which is included with Python, so no external package installation is required.

## Installation

1.  **Copy the Script:**
    Place the `v_hash.py` script on a directory accessible by the `dbadmin` user on all Vertica nodes. For this example, we'll assume it's located at `/home/dbadmin/vertica_pyudx/v_hash/v_hash.py`.

2.  **Create the Library and Function:**
    Run the following SQL commands in `vsql` or your preferred Vertica client. This script creates the library pointing to the Python file and then defines the `v_hash` function from that library.

    ```sql
    -- Create a library for the v_hash Python UDX.
    -- IMPORTANT: Update the path to reflect the actual location of 'v_hash.py' on your Vertica nodes.
    CREATE OR REPLACE LIBRARY VerticaExtPy_V_Hash AS '/home/dbadmin/vertica_pyudx/v_hash/v_hash.py' LANGUAGE 'Python';

    -- Create the scalar function, linking it to the factory in the library.
    CREATE OR REPLACE FUNCTION public.v_hash AS LANGUAGE 'Python' NAME 'v_hash_factory' LIBRARY VerticaExtPy_V_Hash FENCED;
    ```
    
    You can also execute the provided `install.sql` file after ensuring the path within the file is correct for your environment.

3.  **Grant Privileges (Optional):**
    To allow other users to execute the function, grant them the necessary privileges:

    ```sql
    GRANT EXECUTE ON FUNCTION public.v_hash TO PUBLIC;
    ```

## Usage

The `v_hash` function takes a single string argument and returns its SHA256 hash as a 64-character uppercase string.

**Syntax:**
`v_hash(string_to_hash)`

*   `string_to_hash` (VARCHAR): The input string you want to hash.

**Example:**

```sql
-- Example: Hashing a simple string
SELECT v_hash('hello world');
```
Output:
```
                               v_hash
------------------------------------------------------------------
 B94D27B9934D3E08A52E52D7DA7DABFAC484EFEB95214DB6C60D2D016B971AD4
(1 row)
```

**Example with table data:**
```sql
-- Example: Hashing data from a table column
CREATE TABLE users (id INT, username VARCHAR(50));
INSERT INTO users VALUES (1, 'alice'), (2, 'bob');
COMMIT;

SELECT id, username, v_hash(username) AS hashed_username FROM users;
```
Output:
```
 id | username |                          hashed_username
----+----------+------------------------------------------------------------------
  1 | alice    | 8032435422263462153396223472099446976953958569475493359843334338
  2 | bob      | 9F3543162751356A55039EBEC20B32A9996B3E6067727116D3A020721869814C
(2 rows)
```

## Uninstallation

To remove the function and library from your database, run the `uninstall.sql` script or execute the following command:

```sql
DROP LIBRARY IF EXISTS VerticaExtPy_V_Hash CASCADE;
```
This command removes the library and any functions that depend on it.
