import requests
import vertica_sdk


class v_sentiment(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def tag_sentiment(self, session, eduction_service: str, text: str):
        vibe_result = "neutral"
        try:
            z_score = 0.0
            zmatch = 0.0
            doc = session.post(
                eduction_service,
                data={
                    "action": "EduceFromText",
                    "text": text,
                    "responseformat": "simplejson",
                },
            ).json()
            if doc["autnresponse"]["response"].upper() == "SUCCESS":
                if doc["autnresponse"]["responsedata"]["numhits"] > "0":
                    hits = doc["autnresponse"]["responsedata"]["hit"]
                    for hit in hits:
                        this_score = float(hit["score"])
                        if this_score > 0.05:
                            zmatch = zmatch + 1
                        if this_score > 1.70:
                            this_score = 1.70
                        if "positive" in hit["entity_name"]:
                            z_score = z_score + this_score * (this_score + 1) * 0.5
                        if "negative" in hit["entity_name"]:
                            z_score = (
                                z_score + (-1) * this_score * (this_score + 1) * 0.5
                            )
                    if abs(z_score) > (0.35 * (zmatch**0.5)):
                        if z_score > 0:
                            vibe_result = "positive"
                        else:
                            vibe_result = "negative"
                    else:
                        if zmatch > 1:
                            vibe_result = "mixed"
            else:
                return vibe_result
            return vibe_result
        except Exception as err:
            return vibe_result

    def processBlock(self, server_interface, arg_reader, res_writer):
        session = requests.Session()
        url = arg_reader.getString(0)
        while True:
            text = arg_reader.getString(1)
            result = self.tag_sentiment(session, url, text)
            res_writer.setString(result)
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_sentiment_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_sentiment()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addAny()
        arg_types.addAny()
        return_type.addVarchar()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addVarchar(100)
