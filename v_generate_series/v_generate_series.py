import vertica_sdk
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class v_generate_series(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def generate_time_series(self, start_time_str, end_time_str, interval):
        TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        interval_map = {
            "S": {"type": "fixed", "delta": timedelta(seconds=1)},
            "MI": {"type": "fixed", "delta": timedelta(minutes=1)},
            "H": {"type": "fixed", "delta": timedelta(hours=1)},
            "D": {"type": "fixed", "delta": timedelta(days=1)},
            "W": {"type": "fixed", "delta": timedelta(weeks=1)},
            "M": {"type": "variable", "delta_func": lambda: relativedelta(months=1)},
            "Q": {"type": "variable", "delta_func": lambda: relativedelta(months=3)},
            "Y": {"type": "variable", "delta_func": lambda: relativedelta(months=12)},
        }

        if interval not in interval_map:
            raise ValueError(
                f"Invalid interval selection: {interval}. Please select from: seconds (S), minutes (MI), hours (H), days (D), weeks (W), months (M), quarters (Q), years (Y)."
            )

        start_time = datetime.strptime(start_time_str, TIME_FORMAT)
        end_time = datetime.strptime(end_time_str, TIME_FORMAT)

        series = []
        current_time = start_time
        interval_info = interval_map[interval]

        while current_time <= end_time:
            series.append(current_time)

            if interval_info["type"] == "fixed":
                current_time += interval_info["delta"]
            else:
                current_time += interval_info["delta_func"]()

        return series

    def processBlock(self, server_interface, arg_reader, res_writer):

        while True:
            sdate = arg_reader.getString(0)
            edate = arg_reader.getString(1)
            interval = arg_reader.getString(2)
            series_m = self.generate_time_series(sdate, edate, interval)
            res_writer.setArray(series_m)
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_generate_series_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_generate_series()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addVarchar()
        arg_types.addVarchar()
        arg_types.addVarchar()
        return_type.addArrayType(vertica_sdk.ColumnTypes.makeTimestampTz())

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addArrayType(vertica_sdk.ColumnTypes.makeTimestampTz(), 1024)
