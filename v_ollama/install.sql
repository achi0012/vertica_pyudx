CREATE OR REPLACE LIBRARY VerticaExtPy_V_Ollama_Embedding AS 
    '/home/dbadmin/vertica_pyudx/v_ollama/v_ollama.py' 
    depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' LANGUAGE 'Python';
CREATE OR REPLACE FUNCTION public.v_ollama_embedding AS LANGUAGE 'Python' NAME 'v_ollama_embedding_factory' LIBRARY VerticaExtPy_V_Ollama_Embedding fenced;
