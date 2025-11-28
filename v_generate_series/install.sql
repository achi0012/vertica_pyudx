CREATE OR REPLACE LIBRARY VerticaExtPy_V_Generate_Series AS 
    '/home/dbadmin/vertica_pyudx/v_generate_series/v_generate_series.py' 
    depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' LANGUAGE 'Python';
CREATE OR REPLACE FUNCTION public.v_generate_series AS LANGUAGE 'Python' NAME 'v_generate_series_factory' LIBRARY VerticaExtPy_V_Generate_Series fenced;
