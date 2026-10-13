# src/lexer.py
import re


class TokenType:
    # Keyword bahasa Sunda
    MIMITI = 'MIMITI'           # mimiti        -> start program
    TUNGTUNGNA = 'TUNGTUNGNA'   # tungtungna    -> end program
    TINGALIKEUN = 'TINGALIKEUN' # tingalikeun   -> print
    UPAMI = 'UPAMI'             # upami         -> if
    LAMUN_HENTE = 'LAMUN_HENTE' # lamun_hente   -> else
    ARI = 'ARI'                 # ari           -> while
    ANGGEUS = 'ANGGEUS'         # anggeus       -> end (penutup blok if/while)

    # Literal & identifier
    IDENTIFIER = 'IDENTIFIER'
    NUMBER = 'NUMBER'
    STRING = 'STRING'

    # Operator
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    STAR = 'STAR'
    SLASH = 'SLASH'
    PERSEN = 'PERSEN'
    ASSIGN = 'ASSIGN'
    EQ = 'EQ'
    NEQ = 'NEQ'
    GTE = 'GTE'
    LTE = 'LTE'
    GT = 'GT'
    LT = 'LT'

    # Simbol
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    COMMA = 'COMMA'
    COLON = 'COLON'

    NEWLINE = 'NEWLINE'
    EOF = 'EOF'


KEYWORDS = {
    'mimiti': TokenType.MIMITI,
    'tungtungna': TokenType.TUNGTUNGNA,
    'tingalikeun': TokenType.TINGALIKEUN,
    'upami': TokenType.UPAMI,
    'lamun_hente': TokenType.LAMUN_HENTE,
    'ari': TokenType.ARI,
    'anggeus': TokenType.ANGGEUS,
}


class Token:
    __slots__ = ('type', 'value', 'line', 'col')

    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, baris={self.line}, kol={self.col})"


class LexerError(Exception):
    """Dilempar saat lexer menemukan karakter yang tidak dikenali."""
    pass


# Aturan token dalam bentuk regex. Urutan penting: yang lebih spesifik
# (operator 2-karakter seperti '==') harus dicek SEBELUM yang 1-karakter ('=').
TOKEN_SPEC = [
    ('SKIP_COMMENT', r'\#.*'),
    ('SKIP_WS',      r'[ \t]+'),
    ('STRING',       r'"[^"\n]*"|\'[^\'\n]*\''),
    ('NUMBER',       r'\d+(\.\d+)?'),
    ('IDENT',        r'[A-Za-z_][A-Za-z0-9_]*'),
    ('EQ',           r'=='),
    ('NEQ',          r'!='),
    ('GTE',          r'>='),
    ('LTE',          r'<='),
    ('ASSIGN',       r'='),
    ('GT',           r'>'),
    ('LT',           r'<'),
    ('PLUS',         r'\+'),
    ('MINUS',        r'-'),
    ('STAR',         r'\*'),
    ('SLASH',        r'/'),
    ('PERSEN',       r'%'),
    ('LPAREN',       r'\('),
    ('RPAREN',       r'\)'),
    ('COMMA',        r','),
    ('COLON',        r':'),
    ('MISMATCH',     r'.'),
]

MASTER_REGEX = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
)

_SIMPLE_TYPE_MAP = {
    'EQ': TokenType.EQ, 'NEQ': TokenType.NEQ, 'GTE': TokenType.GTE,
    'LTE': TokenType.LTE, 'ASSIGN': TokenType.ASSIGN, 'GT': TokenType.GT,
    'LT': TokenType.LT, 'PLUS': TokenType.PLUS, 'MINUS': TokenType.MINUS,
    'STAR': TokenType.STAR, 'SLASH': TokenType.SLASH, 'PERSEN': TokenType.PERSEN,
    'LPAREN': TokenType.LPAREN, 'RPAREN': TokenType.RPAREN,
    'COMMA': TokenType.COMMA, 'COLON': TokenType.COLON,
}


def tokenize(code: str):
    """Mengubah source code menjadi list of Token, diakhiri token EOF.

    Setiap baris fisik diakhiri satu token NEWLINE (kecuali baris kosong/
    komentar), karena SundaLang adalah bahasa yang statement-nya
    dipisahkan per baris (mirip Python).
    """
    tokens = []
    last_line = 1

    for line_no, raw_line in enumerate(code.split('\n'), start=1):
        last_line = line_no
        col = 1
        pos = 0
        emitted_any = False

        while pos < len(raw_line):
            match = MASTER_REGEX.match(raw_line, pos)
            if not match:
                raise LexerError(f"Karakter tidak dikenal di baris {line_no}, kolom {col}")

            kind = match.lastgroup
            text = match.group()
            start_col = pos + 1
            pos = match.end()

            if kind == 'SKIP_WS':
                col = pos + 1
                continue
            if kind == 'SKIP_COMMENT':
                break  # sisa baris adalah komentar, abaikan
            if kind == 'MISMATCH':
                raise LexerError(
                    f"Karakter tidak dikenal '{text}' di baris {line_no}, kolom {start_col}"
                )

            if kind == 'STRING':
                tokens.append(Token(TokenType.STRING, text[1:-1], line_no, start_col))
            elif kind == 'NUMBER':
                value = float(text) if '.' in text else int(text)
                tokens.append(Token(TokenType.NUMBER, value, line_no, start_col))
            elif kind == 'IDENT':
                if text in KEYWORDS:
                    tokens.append(Token(KEYWORDS[text], text, line_no, start_col))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, text, line_no, start_col))
            else:
                tokens.append(Token(_SIMPLE_TYPE_MAP[kind], text, line_no, start_col))

            emitted_any = True
            col = pos + 1

        if emitted_any:
            tokens.append(Token(TokenType.NEWLINE, '\\n', line_no, col))

    tokens.append(Token(TokenType.EOF, None, last_line + 1, 1))
    return tokens


# Backward-compatible alias (nama lama dipanggil di main.py versi awal)
def lexer(code: str):
    return tokenize(code)
