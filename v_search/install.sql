CREATE OR REPLACE LIBRARY VerticaExtPy_V_Search AS 
    '/home/dbadmin/vertica_pyudx/v_search/v_search.py' LANGUAGE 'Python';
CREATE OR REPLACE FUNCTION public.v_search AS LANGUAGE 'Python' NAME 'v_search_factory' LIBRARY VerticaExtPy_V_Search fenced;
CREATE OR REPLACE FUNCTION public.v_search_text AS LANGUAGE 'Python' NAME 'v_search_text_factory' LIBRARY VerticaExtPy_V_Search fenced;
