# Agent Working Doc for Vertica UDX

## Project structure

7 standalone UDX modules, each in its own `v_*` directory:
- `v_cosine_similarity` / `v_generate_series` / `v_hash` / `v_ollama` / `v_search` / `v_sentiment` / `v_vault`

Each directory contains exactly one Python UDX file plus `install.sql`, `uninstall.sql`, `README.md`.
Every `.py` file defines a `ScalarFunction` subclass and a `ScalarFunctionFactory` subclass. `v_search.py` houses two UDX functions (`v_search`, `v_search_text`).

There is no `src/` or `tests/` directory, no build system, no test framework, no lint config. The repo is a pure collection of scripts deployed to a Vertica server.

## UDX pattern (all modules follow this)

```python
import vertica_sdk

class v_<name>(vertica_sdk.ScalarFunction):
    def processBlock(self, srv_iface, arg_reader, res_writer):
        while True:
            # read input, compute, write output
            res_writer.next()
            if not arg_reader.next():
                break

class v_<name>_factory(vertica_sdk.ScalarFunctionFactory):
    def createScalarFunction(self, srv): return v_<name>()
    def getPrototype(self, srv_iface, arg_types, return_type): ...
    def getReturnType(self, srv_iface, arg_types, return_type): ...
```

`vertica_sdk` is provided by the Vertica server runtime (not pip-installable).

## SQL deployment (install.sql)

```sql
CREATE OR REPLACE LIBRARY VerticaExtPy_V_<Name> AS '<server_path>/v_<name>.py' LANGUAGE 'Python';
CREATE OR REPLACE FUNCTION public.v_<name> AS LANGUAGE 'Python' NAME '<name>_factory' LIBRARY VerticaExtPy_V_<Name> fenced;
```

`install.sql` paths reference a hardcoded server directory `/home/dbadmin/vertica_pyudx/`. Adjust path before deploying.

## Dependencies per module

| Module | Deps |
|---|---|
| v_cosine_similarity | none (stdlib only) |
| v_generate_series | `python-dateutil` |
| v_hash | `requests` (unused dead import) |
| v_ollama | `ollama` |
| v_search | none (stdlib only) |
| v_sentiment | `requests` |
| v_vault | none (stdlib only) |

## Known code issues to watch for

- `v_hash.py` imports `requests` at line 1 — it is never used.

- Code uses no type annotations.
- Most classes/methods lack docstrings (except `v_search.py`).
- Errors are handled with bare `except Exception: return default` rather than specific exceptions.
- `v_vault` reads `/opt/vertica/config/apikeys.dat` (only exists on Vertica server).
