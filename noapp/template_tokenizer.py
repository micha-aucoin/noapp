
class TokenKind:
    TEXT = "TEXT"
    VARIABLE = "VARIABLE"
    BLOCK = "BLOCK"
    
class Token:
    def __init__(self, kind: TokenKind, value: str | None = None):
        self.kind = kind
        self.value = value

    def __repr__(self) -> str:
        if self.value:
            return f"Token({self.kind}: {self.value})"
        else:
            return f"Token({self.kind})"

def tokenizer(text: str) -> list[Token]:
    char = iter(text)

    buffer = ""
    tokens = []
    current_char = next(char, None)

    # MAIN LOOP: Find tokens
    while current_char is not None:

        if current_char == '{':
            next_char = next(char, None)

            if next_char == '{':
                # Save any normal text we collected first
                if buffer:
                    tokens.append(Token(TokenKind.TEXT, buffer))
                    buffer = ""

                # current_char = '{'
                # next_char = '{'
                current_char = next(char, None)

                # VARIABLE LOOP: Read until }}
                while current_char is not None:
                    if current_char == '}':
                        next_char = next(char, None)
                        if next_char == '}':
                            tokens.append(Token(TokenKind.VARIABLE, buffer.strip()))
                            buffer = ""
                            current_char = next(char, None)
                            break # break VARIALBE loop
                        buffer += current_char
                        current_char = next_char
                        continue # reset VARIALBE loop
                    buffer += current_char
                    current_char = next(char, None)

                continue # reset MAIN loop

            elif next_char == '%':
                # Save any normal text we collected first
                if buffer:
                    tokens.append(Token(TokenKind.TEXT, buffer))
                    buffer = ""

                # current_char = '{'
                # next_char = '%'
                current_char = next(char, None)

                # BLOCK LOOP: Read until %}
                while current_char is not None:
                    if current_char == '%':
                        next_char = next(char, None)
                        if next_char == '}':
                            tokens.append(Token(TokenKind.BLOCK, buffer.strip()))
                            buffer = ""
                            current_char = next(char, None)
                            break # break BLOCK loop
                        buffer += current_char
                        current_char = next_char
                        continue # reset BLOCK loop
                    buffer += current_char
                    current_char = next(char, None)

                continue # reset MAIN loop

            else:
                buffer += current_char
                current_char = next_char
                continue # reset MAIN loop

        buffer += current_char
        current_char = next(char, None)

    if buffer:
        tokens.append(Token(TokenKind.TEXT, buffer))
    return tokens


