from .template_tokenizer import TokenKind

class TextNode:
    def __init__(self, value: str):
        self.value: str = value
    def __repr__(self) -> str:
        return f"TextNode(value={self.value})"

class VariableNode:
    def __init__(self, expression: str):
        self.expression: str = expression
    def __repr__(self) -> str:
        return f"VariableNode(expression={self.expression})"

class FunctionCallNode:
    def __init__( self, function_name: str, args: str):
        self.function_name = function_name
        self.args = args
    def __repr__(self) -> str:
        return f"FunctionCallNode(function_name={self.function_name}, args={self.args})"

class MethodCallNode:
    def __init__(self, object_expression: str, method_name: str, args: str):
        self.object_expression: str = object_expression
        self.method_name: str = method_name
        self.args: str = args
    def __repr__(self) -> str:
        return f"MethodCallNode(object_expression={self.object_expression}, method_name={self.method_name}, args={self.args})"

class ExtendsNode:
    def __init__(self, filename: str):
        self.filename: str = filename
    def __repr__(self) -> str:
        return f"ExtendsNode(filename={self.filename})"

class BlockNode:
    def __init__(self, name: str, children: list):
        self.name: str = name
        self.children: list = children
    def __repr__(self) -> str:
        return f"BlockNode(name={self.name}, children={self.children})"

class ForNode:
    def __init__(self, item_name: str, iterable_name: str, children: list):
        self.item_name: str = item_name
        self.iterable_name: str = iterable_name
        self.children: list = children
    def __repr__(self) -> str:
        return f"ForNode(item_name={self.item_name}, iterable_name={self.iterable_name}, children={self.children})"

def resolve(expression: str, context: dict):
    parts = expression.strip().split(".")
    current = context[parts[0]]
    for part in parts[1:]:
        current = getattr(current, part)
    return current

def parser(tokens):
    nodes = []
    index = 0

    while index < len(tokens):
        token = tokens[index]
        match token.kind:

            case TokenKind.TEXT:
                nodes.append(TextNode(value=token.value))

            case TokenKind.VARIABLE:
                expression = token.value
                if "(" in expression and expression.endswith(")"):
                    name, args = expression.split("(", 1)
                    args = args[:-1]
                    if "." not in name:
                        nodes.append(FunctionCallNode(function_name=name, args=args))
                    else:
                        object_expression, method_name = name.rsplit(".", 1)
                        nodes.append(MethodCallNode(object_expression, method_name, args))
                else:
                    nodes.append(VariableNode(expression=expression))

            case TokenKind.BLOCK:
                parts = token.value.split()
                match parts[0]:

                    case "extends":
                        filename = parts[1].strip("'\"")
                        nodes.append(ExtendsNode(filename=filename))

                    case "block":
                        # breakpoint()
                        # (Pdb) n;; l;; pp locals()
                        name = parts[1]
                        block_tokens = []
                        index += 1
                        while index < len(tokens):
                            current = tokens[index]
                            if current.kind == TokenKind.BLOCK:
                                current_parts = current.value.split()
                                if current_parts[0] == "endblock":
                                    break
                            block_tokens.append(current)
                            index += 1
                        children = parser(block_tokens)
                        nodes.append(BlockNode(name=name, children=children))

                    case "for":
                        # breakpoint()
                        # (Pdb) n;; l;; pp locals()
                        item_name = parts[1]
                        iterable_name = parts[3]
                        block_tokens = []
                        index += 1
                        while index < len(tokens):
                            current = tokens[index]
                            if current.kind == TokenKind.BLOCK:
                                current_parts = current.value.split()
                                if current_parts[0] == "endfor":
                                    break
                            block_tokens.append(current)
                            index += 1
                        children = parser(block_tokens)
                        nodes.append(ForNode(item_name=item_name, iterable_name=iterable_name, children=children))
        index += 1
    return nodes


def render_nodes(nodes: list, context: dict):
    result = ""
    for node in nodes:

        # TEXT NODE
        if isinstance(node, TextNode):
            result += node.value

        # VARIABLE NODE
        if isinstance(node, VariableNode):
            value = resolve(expression=node.expression, context=context)
            result += str(value)

        # METHOD CALL NODE
        if isinstance(node, MethodCallNode):
            obj = resolve(expression=node.object_expression, context=context)
            method = getattr(obj, node.method_name)
            args = node.args.strip("'\"")
            if args:
                result += str(method(args))
            else:
                result += str(method())

        # FUNCTION CALL NODE
        if isinstance(node, FunctionCallNode):
            function = context[node.function_name]
            pargs = []
            kwargs = {}
            for arg in node.args.split(","):
                arg = arg.strip()
                if not arg:
                    continue
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    kwargs[key.strip()] = resolve(expression=value, context=context)
                else:
                    pargs.append(arg.strip("'\""))
            result += str(function(*pargs, **kwargs))

        # FOR NODE
        if isinstance(node, ForNode):
            # breakpoint()
            # (Pdb) n;; l;; pp locals()
            items = resolve(expression=node.iterable_name, context=context)
            for item in items:
                # loop_context = {} <- this fails tests
                loop_context = context.copy()
                # add the current item to loop_context dict
                # VariableNode will get an updated item on each iteraction
                loop_context[node.item_name] = item
                # handle all the child nodes inside the for block
                result += render_nodes(node.children, loop_context)

        # BLOCK NODE
        if isinstance(node, BlockNode):
            # breakpoint()
            # (Pdb) n;; l;; pp locals()
            result += render_nodes(node.children, context)

    return result

