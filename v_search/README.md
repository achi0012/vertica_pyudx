# Installation Guide for v_search and v_search_text Vertica UDXs

This document outlines the steps to install and use the `v_search` and `v_search_text` User-Defined Extensions (UDXs) in Vertica. These UDXs allow you to perform advanced text searches within Vertica.

## Prerequisites

*   A running Vertica database.
*   Sufficient privileges to create functions and libraries in Vertica.

## Installation Steps

1.  **Create the Library:**

First, you need to create a library in Vertica that points to the location of your Python script (`v_search.py`). Make sure the file is accessible by the Vertica server.

```sql
CREATE OR REPLACE LIBRARY VerticaExtPy_V_Search AS
'/home/dbadmin/vertica_pyudx/v_search/v_search.py' LANGUAGE 'Python';
```

*   Replace `/home/dbadmin/vertica_pyudx/v_search/v_search.py` with the actual path to your `v_search.py` file on the Vertica server, including the trailing `/*` to ensure all packages are loaded.

2.  **Create the Functions:**

Now, create the scalar functions in Vertica, associating them with the library you just created.

```sql
CREATE OR REPLACE FUNCTION public.v_search AS LANGUAGE 'Python' NAME 'v_search_factory' LIBRARY VerticaExtPy_V_Search fenced;
CREATE OR REPLACE FUNCTION public.v_search_text AS LANGUAGE 'Python' NAME 'v_search_text_factory' LIBRARY VerticaExtPy_V_Search fenced;
```

3.  **Grant Usage Privileges (if necessary):**

If other users need to use these functions, grant them usage privileges on the library and execute privileges on the functions:

```sql
GRANT USAGE ON LIBRARY VerticaExtPy_V_Search TO PUBLIC; -- Or to specific users/roles
GRANT EXECUTE ON FUNCTION public.v_search TO PUBLIC; -- Or to specific users/roles
GRANT EXECUTE ON FUNCTION public.v_search_text TO PUBLIC; -- Or to specific users/roles
```

## `v_search` Function

The `v_search` function allows you to perform complex searches using a custom query language that supports `AND`, `OR`, `NOT`, and parentheses.

**Syntax:**

`v_search(condition, text)`

*   `condition`: The search condition string (e.g., " ( word1 AND word2 ) OR ( NOT word3 ) "). The search is case-insensitive.
*   `text`: The text to search within.

The function returns `true` if the text meets the condition, and `false` otherwise.

**Example:**

```sql
SELECT v_search('(vertica AND (sql OR python)) AND NOT (hadoop)', 'This is a text about Vertica and SQL.');
```

## `v_search_text` Function

The `v_search_text` function provides a simplified interface for common search scenarios.

**Syntax:**

`v_search_text(ianywords, iallwords, eallwords, text)`

*   `ianywords`: A comma-separated string of words. The condition is true if **any** of these words are in the text.
*   `iallwords`: A comma-separated string of words. The condition is true if **all** of these words are in the text.
*   `eallwords`: A comma-separated string of words. The condition is true if **none** of these words are in the text.
*   `text`: The text to search within.

All parameters are case-insensitive.

**Example:**

```sql
SELECT v_search_text('vertica,sql', 'database', 'hadoop,spark', 'This text is about the Vertica database.');
```
This would return `true` because "vertica" is present, "database" is present, and neither "hadoop" nor "spark" are present.

## Notes
*   These UDXs return a boolean value.
*   Ensure that the Python script (`v_search.py`) is compatible with the Vertica Python environment.
