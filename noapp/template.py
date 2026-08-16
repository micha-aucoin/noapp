import re
from pathlib import Path
from .template_tokenizer import tokenizer
from .template_parser import parser, render_nodes, ExtendsNode, BlockNode


class Template:
    def __init__(
        self,
        directory: str | None = None,
    ):
        if directory:
            self.directory = Path(directory)
        else:
            self.directory = None

    def response(self, filename, **context):
        source = (self.directory / filename).read_text()
        nodes = parser(tokenizer(source))

        extends_node = None
        for node in nodes:
            if isinstance(node, ExtendsNode):
                extends_node = node
                break
        if extends_node is not None:
            # breakpoint()
            # (Pdb) n;; l;; pp locals()
            parent_source = (self.directory / extends_node.filename).read_text()
            parent_nodes = parser(tokenizer(parent_source))
            for child_node in nodes:
                if isinstance(child_node, BlockNode):
                    for parent_node in parent_nodes:
                        if (
                            isinstance(parent_node, BlockNode)
                            and parent_node.name == child_node.name
                        ):
                            parent_node.children = child_node.children
                            break
            nodes = parent_nodes

        return render_nodes(nodes, context)


