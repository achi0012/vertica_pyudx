import base64
import hashlib
import json
import os
import vertica_sdk


class v_vault(vertica_sdk.ScalarFunction):

    vertica_api_key = None
    _APIKEY_FILE = "/opt/vertica/config/apikeys.dat"

    def __init__(self):
        self._load_api_key()

    def _load_api_key(self):
        if v_vault.vertica_api_key is not None:
            return

        if not os.path.exists(self._APIKEY_FILE):
            return

        try:
            with open(self._APIKEY_FILE, "r", encoding="utf-8") as infile:
                data = json.load(infile)
        except (OSError, json.JSONDecodeError):
            return

        if isinstance(data, list) and data:
            first_entry = data[0]
            if isinstance(first_entry, dict) and "apikey" in first_entry:
                v_vault.vertica_api_key = first_entry["apikey"]

    def setup(self, server_interface, col_types):
        self._load_api_key()

    def e_string(self, text):
        if not v_vault.vertica_api_key:
            return ""

        key = hashlib.sha256(v_vault.vertica_api_key.encode("utf-8")).digest()
        data = text.encode("utf-8")
        encrypted = bytearray()
        for index, value in enumerate(data):
            encrypted.append(value ^ key[index % len(key)])

        return base64.urlsafe_b64encode(bytes(encrypted)).decode("ascii").rstrip("=")

    def d_string(self, text):
        if not v_vault.vertica_api_key:
            return ""

        padded_text = text + "=" * (-len(text) % 4)
        try:
            encrypted_data = base64.urlsafe_b64decode(padded_text)
        except (ValueError, TypeError):
            return ""

        key = hashlib.sha256(v_vault.vertica_api_key.encode("utf-8")).digest()
        decrypted = bytearray()
        for index, value in enumerate(encrypted_data):
            decrypted.append(value ^ key[index % len(key)])

        try:
            return decrypted.decode("utf-8")
        except UnicodeDecodeError:
            return ""

    def processBlock(self, server_interface, arg_reader, res_writer):
        while True:
            method = arg_reader.getString(0).lower()
            text = arg_reader.getString(1)
            result = None
            if method == "e":
                result = self.e_string(text)
            elif method == "d":
                result = self.d_string(text)
            res_writer.setString(result)
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_vault_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_vault()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addAny()
        arg_types.addAny()
        return_type.addVarchar()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addVarchar(64)
