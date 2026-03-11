import requests
import hashlib
import vertica_sdk


class v_hash(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def hash_string(self, text):
        # using sha256b to hash the input string and return the first 64 characters (32 bytes)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:64].upper()

    def processBlock(self, server_interface, arg_reader, res_writer):
        while True:
            text = arg_reader.getString(0)
            res_writer.setString(self.hash_string(text))
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_hash_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_hash()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addAny()
        return_type.addVarchar()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addVarchar(64)
