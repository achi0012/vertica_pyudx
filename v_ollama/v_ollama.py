import vertica_sdk
from ollama import Client


class v_ollama_embedding(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def processBlock(self, server_interface, arg_reader, res_writer):
        host = arg_reader.getString(0)
        model = arg_reader.getString(1)
        dimension = arg_reader.getInt(2)
        client = Client(host=host)
        while True:
            text = arg_reader.getString(3)
            result = client.embed(model=model, dimensions=dimension, input=text)
            res_writer.setArray(result["embeddings"][0])
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_ollama_embedding_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_ollama_embedding()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addVarchar()
        arg_types.addVarchar()
        arg_types.addInt()
        arg_types.addVarchar()
        return_type.addArrayType(vertica_sdk.ColumnTypes.makeFloat())

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addArrayType(vertica_sdk.ColumnTypes.makeFloat(), 4096)
