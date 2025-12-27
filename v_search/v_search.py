import re
import vertica_sdk


class ConditionEvaluator:
    """
    Judges whether a piece of text meets the specified search criteria.
    Search criteria can include AND, OR, NOT, and parentheses.
    Operators (AND, OR, NOT) and Operands should ideally be separated by spaces.
    Parentheses can be adjacent to other tokens (e.g., "(A AND B)OR C").
    Operands are treated as case-insensitive. Operators (AND, OR, NOT) are case-sensitive.
    """

    def check_condition(self, condition: str, text: str) -> bool:
        """
        Checks if the text meets the condition.

        :param condition: The search condition string, e.g., " ( A AND B ) OR ( NOT C ) "
        :param text: The text to search within.
        :param variables: A dictionary mapping variable names (e.g., "A", "B", "C") to boolean values.
        :return: A boolean indicating whether the text meets the condition.
        :raises ValueError: If the condition string is malformed.
        """
        return self._evaluate(condition, text)

    def _evaluate(self, condition: str, text: str) -> bool:
        condition = condition.strip()
        if not condition:
            return True  # An empty condition is always true.

        postfix = self._infix_to_postfix(condition)
        stack = []
        lower_text = text.lower()

        for token in postfix.split():
            if token == "AND":
                if len(stack) < 2:
                    raise ValueError(
                        "Invalid condition format: insufficient operands for AND."
                    )
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(operand1 and operand2)
            elif token == "OR":
                if len(stack) < 2:
                    raise ValueError(
                        "Invalid condition format: insufficient operands for OR."
                    )
                operand2 = stack.pop()
                operand1 = stack.pop()
                stack.append(operand1 or operand2)
            elif token == "NOT":
                if not stack:
                    raise ValueError(
                        "Invalid condition format: insufficient operands for NOT."
                    )
                operand = stack.pop()
                stack.append(not operand)
            # elif token in variables:
            #     stack.append(variables[token])
            else:
                # Assume it is a text variable, check for containment.
                stack.append(token.lower() in lower_text)

        if len(stack) != 1:
            raise ValueError("Invalid condition format: too many operands.")

        return stack.pop()

    def _infix_to_postfix(self, expression: str) -> str:
        operator_stack = []
        postfix = []

        # Add spaces around parentheses to ensure they split correctly
        spaced_expression = expression.replace("(", " ( ").replace(")", " ) ")
        tokens = [token for token in spaced_expression.strip().split() if token]

        for token in tokens:
            if token == "(":
                operator_stack.append(token)
            elif token == ")":
                while operator_stack and operator_stack[-1] != "(":
                    postfix.append(operator_stack.pop())
                if not operator_stack:
                    raise ValueError(
                        "Invalid condition format: mismatched parentheses."
                    )
                operator_stack.pop()  # Pop the "("
            elif token == "NOT":
                operator_stack.append(token)
            elif token == "AND":
                while operator_stack and self._precedence(
                    operator_stack[-1]
                ) >= self._precedence(token):
                    postfix.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == "OR":
                while operator_stack and self._precedence(
                    operator_stack[-1]
                ) >= self._precedence(token):
                    postfix.append(operator_stack.pop())
                operator_stack.append(token)
            else:
                postfix.append(token)  # Operand

        while operator_stack:
            if operator_stack[-1] == "(":
                raise ValueError("Invalid condition format: mismatched parentheses.")
            postfix.append(operator_stack.pop())

        return " ".join(postfix)

    def _precedence(self, operator: str) -> int:
        if operator == "NOT":
            return 3
        elif operator == "AND":
            return 2
        elif operator == "OR":
            return 1
        elif operator == "(":
            return 0
        else:
            return -1  # variable


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
            condi = ""
            if ianywords:
                any_list = [
                    word.strip() for word in ianywords.split(",") if word.strip()
                ]
                condi += " ( " + " OR ".join(any_list) + " ) "
            if iallwords:
                all_list = [
                    word.strip() for word in iallwords.split(",") if word.strip()
                ]
                if condi:
                    condi += " AND "
                condi += " ( " + " AND ".join(all_list) + " ) "
            if eallwords:
                exclude_list = [
                    word.strip() for word in eallwords.split(",") if word.strip()
                ]
                if condi:
                    condi += " AND "
                condi += (
                    " ( "
                    + " AND ".join([f"NOT {word}" for word in exclude_list])
                    + " ) "
                )
            result = coneval.check_condition(condi, text)
            res_writer.setBool(result)
            res_writer.next()
            if not arg_reader.next():
                # Stop processing when there are no more input rows.
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
