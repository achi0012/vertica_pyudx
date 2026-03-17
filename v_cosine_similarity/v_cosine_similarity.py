import vertica_sdk
import json
import math


class v_cosine_similarity(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def caculate(self, text1, text2):
        # text1 is json array string, text2 is json array string
        # convert text1 , text2 to array

        vec1 = json.loads(text1)
        vec2 = json.loads(text2)

        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return float(dot_product / (magnitude1 * magnitude2))

    def processBlock(self, server_interface, arg_reader, res_writer):
        while True:
            text0 = arg_reader.getString(0)
            text1 = arg_reader.getString(1)
            res_writer.setString(self.caculate(text0, text1))
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_cosine_similarity_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_cosine_similarity()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addVarchar()
        arg_types.addVarchar()
        return_type.addFloat8()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addFloat8()
