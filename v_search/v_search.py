import vertica_sdk


class ConditionEvaluator:
    _PREC = {"NOT": 3, "AND": 2, "OR": 1, "(": 0}

    def check_condition(self, condition, text):
        return self._evaluate(condition, text)

    def _evaluate(self, condition, text):
        condition = condition.strip()
        if not condition:
            return True

        postfix = self._infix_to_postfix(condition)
        stack = []
        lower_text = text.lower()
        token_cache = {}

        for token in postfix.split():
            if token == "AND":
                b, a = stack.pop(), stack.pop()
                stack.append(a and b)
            elif token == "OR":
                b, a = stack.pop(), stack.pop()
                stack.append(a or b)
            elif token == "NOT":
                stack.append(not stack.pop())
            else:
                if token not in token_cache:
                    token_cache[token] = token.lower() in lower_text
                stack.append(token_cache[token])

        if len(stack) != 1:
            raise ValueError("Invalid condition format.")
        return stack.pop()

    def _infix_to_postfix(self, expression):
        operator_stack = []
        postfix = []
        spaced = expression.replace("(", " ( ").replace(")", " ) ")
        tokens = spaced.split()

        for token in tokens:
            if token == "(":
                operator_stack.append(token)
            elif token == ")":
                while operator_stack and operator_stack[-1] != "(":
                    postfix.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError("Invalid condition format: mismatched parentheses.")
                operator_stack.pop()
            elif token == "NOT":
                operator_stack.append(token)
            elif token in self._PREC:
                prec = self._PREC[token]
                while operator_stack and self._PREC.get(operator_stack[-1], -1) >= prec:
                    postfix.append(operator_stack.pop())
                operator_stack.append(token)
            else:
                postfix.append(token)

        while operator_stack:
            if operator_stack[-1] == "(":
                raise ValueError("Invalid condition format: mismatched parentheses.")
            postfix.append(operator_stack.pop())

        return " ".join(postfix)


class v_search(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def processBlock(self, server_interface, arg_reader, res_writer):
        coneval = ConditionEvaluator()
        while True:
            condi = arg_reader.getString(0)
            text = arg_reader.getString(1)
            result = coneval.check_condition(condi, text)
            res_writer.setBool(result)
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
                break

    def destroy(self, server_interface, col_types):
        pass


class v_search_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_search()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addVarchar()
        arg_types.addVarchar()
        return_type.addBool()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addBool()


class v_search_text(vertica_sdk.ScalarFunction):

    def __init__(self):
        pass

    def setup(self, server_interface, col_types):
        pass

    def processBlock(self, server_interface, arg_reader, res_writer):
        coneval = ConditionEvaluator()
        while True:
            ianywords = arg_reader.getString(0)
            iallwords = arg_reader.getString(1)
            eallwords = arg_reader.getString(2)
            text = arg_reader.getString(3)

            parts = []
            if ianywords:
                words = [w.strip() for w in ianywords.split(",") if w.strip()]
                if words:
                    parts.append("( " + " OR ".join(words) + " )")
            if iallwords:
                words = [w.strip() for w in iallwords.split(",") if w.strip()]
                if words:
                    if parts:
                        parts.append(" AND ")
                    parts.append("( " + " AND ".join(words) + " )")
            if eallwords:
                words = [w.strip() for w in eallwords.split(",") if w.strip()]
                if words:
                    if parts:
                        parts.append(" AND ")
                    parts.append("( " + " AND ".join("NOT " + w for w in words) + " )")

            condi = "".join(parts)
            result = coneval.check_condition(condi, text)
            res_writer.setBool(result)
            res_writer.next()
            if not arg_reader.next():
                break

    def destroy(self, server_interface, col_types):
        pass


class v_search_text_factory(vertica_sdk.ScalarFunctionFactory):

    def createScalarFunction(self, srv):
        return v_search_text()

    def getPrototype(self, srv_interface, arg_types, return_type):
        arg_types.addVarchar()
        arg_types.addVarchar()
        arg_types.addVarchar()
        arg_types.addVarchar()
        return_type.addBool()

    def getReturnType(self, srv_interface, arg_types, return_type):
        return_type.addBool()
