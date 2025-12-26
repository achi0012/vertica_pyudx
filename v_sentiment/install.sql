CREATE OR REPLACE LIBRARY VerticaExtPy_V_Sentiment AS 
    '/home/dbadmin/vertica_pyudx/v_sentiment/v_sentiment.py' 
    depends '/home/dbadmin/vertica_pyudx/lib/python3.13/site-packages/*' LANGUAGE 'Python';
CREATE OR REPLACE FUNCTION public.v_sentiment AS LANGUAGE 'Python' NAME 'v_sentiment_factory' LIBRARY VerticaExtPy_V_Sentiment fenced;
