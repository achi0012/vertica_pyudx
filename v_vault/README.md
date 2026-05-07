# v_vault Vertica UDX

This document provides instructions on how to install and use the `v_vault` User-Defined Extension (UDX) in Vertica. The `v_vault` function uses the Vertica server API key file to perform simple encryption and decryption of string values.

## Prerequisites

*   A running Vertica database.
*   The `v_vault.py` script must be accessible from the Vertica server nodes.
*   Sufficient database privileges to create libraries and functions.
*   A valid Vertica API key stored in `/opt/vertica/config/apikeys.dat` on the server.

This UDX uses only Python standard libraries (`hashlib`, `base64`, `json`, and `os`), so no additional packages are required.

## Installation

1.  **Copy the Script:**
    Place the `v_vault.py` script on a directory accessible by the `dbadmin` user on all Vertica nodes. For this example, we assume it is located at `/home/dbadmin/vertica_pyudx/v_vault/v_vault.py`.

2.  **Create the Library and Function:**
    Run the following SQL commands in `vsql` or your preferred Vertica client. This script creates the library pointing to the Python file and then defines the `v_vault` function from that library.

    ```sql
    -- Create a library for the v_vault Python UDX.
    -- IMPORTANT: Update the path to reflect the actual location of 'v_vault.py' on your Vertica nodes.
    CREATE OR REPLACE LIBRARY VerticaExtPy_V_Vault AS '/home/dbadmin/vertica_pyudx/v_vault/v_vault.py' LANGUAGE 'Python';

    -- Create the scalar function, linking it to the factory in the library.
    CREATE OR REPLACE FUNCTION public.v_vault AS LANGUAGE 'Python' NAME 'v_vault_factory' LIBRARY VerticaExtPy_V_Vault FENCED;
    ```

    You can also execute the provided `install.sql` file after ensuring the path within the file is correct for your environment.

3.  **Grant Privileges (Optional):**
    To allow other users to execute the function, grant them the necessary privileges:

    ```sql
    GRANT EXECUTE ON FUNCTION public.v_vault TO PUBLIC;
    ```

## Usage

The `v_vault` function accepts two string arguments:

*   `method` (VARCHAR): Use `'e'` to encrypt or `'d'` to decrypt.
*   `text` (VARCHAR): The input text to encrypt or decrypt.

The function loads the first API key from `/opt/vertica/config/apikeys.dat` and uses it to derive an XOR-based cipher.

**Syntax:**
`v_vault(method, text)`

**Examples:**

```sql
-- Encrypt a string
SELECT v_vault('e', 'my secret') AS encrypted_text;

-- Decrypt the previously encrypted string
SELECT v_vault('d', '<encrypted_value>') AS decrypted_text;
```

**Example with table data:**

```sql
CREATE TABLE secrets (id INT, payload VARCHAR(200));
INSERT INTO secrets VALUES (1, 'hello'), (2, 'world');
COMMIT;

SELECT id,
       v_vault('e', payload) AS encrypted_payload
FROM secrets;
```

## Notes

*   The function reads the first entry from `/opt/vertica/config/apikeys.dat` and uses its `apikey` field.
*   If the API key file is missing or invalid, `e` and `d` methods return an empty string.
*   The encryption is implemented with an XOR cipher and Base64 encoding.

## Uninstallation

To remove the function and library from your database, run the `uninstall.sql` script or execute the following command:

```sql
DROP LIBRARY IF EXISTS VerticaExtPy_V_Vault CASCADE;
```

This command removes the library and any functions that depend on it.
