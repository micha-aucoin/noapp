from pathlib import Path

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
        for key, value in context.items():
            source = source.replace(
                "{{ " + key + " }}",
                str(value)
            )
        return source

