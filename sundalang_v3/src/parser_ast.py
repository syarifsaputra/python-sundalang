# src/parser_ast.py
# ============================================================
# AST NODE DEFINITIONS
# ============================================================

class Node:
    """Base class seluruh AST node, supaya bisa dicek dengan isinstance."""
    pass


class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"ProgramNode({self.statements!r})"


class NumberNode(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"NumberNode({self.value})"


class StringNode(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"StringNode({self.value!r})"


class VarNode(Node):
    """Referensi ke sebuah variabel, misal `angka1` di dalam ekspresi."""
    def __init__(self, name, line):
        self.name = name
        self.line = line

    def __repr__(self):
        return f"VarNode({self.name})"


class BinOpNode(Node):
    """Operasi biner: kiri OP kanan, misal angka1 + angka2."""
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line

    def __repr__(self):
        return f"BinOpNode({self.left!r} {self.op} {self.right!r})"


class UnaryOpNode(Node):
    """Operasi unary: -angka."""
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line

    def __repr__(self):
        return f"UnaryOpNode({self.op}{self.operand!r})"


class AssignNode(Node):
    def __init__(self, var_name, expr, line):
        self.var_name = var_name
        self.expr = expr
        self.line = line

    def __repr__(self):
        return f"AssignNode({self.var_name} = {self.expr!r})"


class PrintNode(Node):
    """tingalikeun bisa menerima banyak ekspresi dipisah koma."""
    def __init__(self, expr_list, line):
        self.expr_list = expr_list
        self.line = line

    def __repr__(self):
        return f"PrintNode({self.expr_list!r})"


class IfNode(Node):
    def __init__(self, condition, then_body, else_body, line):
        self.condition = condition
        self.then_body = then_body          # list of statement nodes
        self.else_body = else_body          # list of statement nodes atau None
        self.line = line

    def __repr__(self):
        return f"IfNode(cond={self.condition!r}, then={len(self.then_body)} stmt, else={'ada' if self.else_body else 'tidak'})"


class WhileNode(Node):
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body = body
        self.line = line

    def __repr__(self):
        return f"WhileNode(cond={self.condition!r}, body={len(self.body)} stmt)"


# ============================================================
# PARSER ERROR
# ============================================================

class ParserError(Exception):
    pass


# ============================================================
# PARSER (Recursive Descent)
# ============================================================

from lexer import TokenType


class Parser:
    def __init__(self, tokens):
        # Buang token NEWLINE yang dobel/di awal tidak perlu; tetap simpan
        # NEWLINE karena dipakai sebagai pemisah statement.
        self.tokens = tokens
        self.pos = 0

    # ---------- helper dasar ----------

    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _advance(self):
        tok = self.tokens[self.pos]
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def _check(self, type_):
        return self._peek().type == type_

    def _match(self, *types):
        if self._peek().type in types:
            return self._advance()
        return None

    def _expect(self, type_, msg=None):
        tok = self._peek()
        if tok.type != type_:
            raise ParserError(
                msg or f"Diharapkan {type_} tapi menemukan {tok.type} ('{tok.value}') "
                       f"di baris {tok.line}"
            )
        return self._advance()

    def _skip_newlines(self):
        while self._check(TokenType.NEWLINE):
            self._advance()

    # ---------- grammar rules ----------

    def parse_program(self):
        """program ::= 'mimiti' NEWLINE statement_list 'tungtungna'"""
        self._skip_newlines()
        self._expect(TokenType.MIMITI, "Program harus dimulai dengan kata 'mimiti'")
        self._skip_newlines()

        statements = self._parse_statement_list(stop_tokens=(TokenType.TUNGTUNGNA,))

        self._expect(TokenType.TUNGTUNGNA, "Program harus diakhiri dengan kata 'tungtungna'")
        self._skip_newlines()
        self._expect(TokenType.EOF, "Ditemukan kode tambahan setelah 'tungtungna'")

        return ProgramNode(statements)

    def _parse_statement_list(self, stop_tokens):
        """Mengumpulkan statement sampai bertemu salah satu stop_tokens."""
        statements = []
        self._skip_newlines()
        while not self._check_any(stop_tokens) and not self._check(TokenType.EOF):
            stmt = self._parse_statement()
            statements.append(stmt)
            self._skip_newlines()
        return statements

    def _check_any(self, types):
        return self._peek().type in types

    def _parse_statement(self):
        tok = self._peek()

        if tok.type == TokenType.TINGALIKEUN:
            return self._parse_print()
        if tok.type == TokenType.UPAMI:
            return self._parse_if()
        if tok.type == TokenType.ARI:
            return self._parse_while()
        if tok.type == TokenType.IDENTIFIER:
            return self._parse_assign()

        raise ParserError(
            f"Statement tidak dikenal: token '{tok.value}' ({tok.type}) di baris {tok.line}"
        )

    def _parse_assign(self):
        """assign_stmt ::= IDENTIFIER '=' expr NEWLINE"""
        name_tok = self._expect(TokenType.IDENTIFIER)
        self._expect(TokenType.ASSIGN, f"Diharapkan '=' setelah '{name_tok.value}' di baris {name_tok.line}")
        expr = self._parse_expr()
        self._end_statement()
        return AssignNode(name_tok.value, expr, name_tok.line)

    def _parse_print(self):
        """print_stmt ::= 'tingalikeun' expr_list NEWLINE"""
        tok = self._expect(TokenType.TINGALIKEUN)
        expr_list = [self._parse_expr()]
        while self._match(TokenType.COMMA):
            expr_list.append(self._parse_expr())
        self._end_statement()
        return PrintNode(expr_list, tok.line)

    def _parse_if(self):
        """if_stmt ::= 'upami' expr NEWLINE statement_list
                       ['lamun_hente' NEWLINE statement_list] 'anggeus'"""
        tok = self._expect(TokenType.UPAMI)
        condition = self._parse_expr()
        self._end_statement()

        then_body = self._parse_statement_list(
            stop_tokens=(TokenType.LAMUN_HENTE, TokenType.ANGGEUS, TokenType.TUNGTUNGNA)
        )

        else_body = None
        if self._match(TokenType.LAMUN_HENTE):
            self._end_statement()
            else_body = self._parse_statement_list(
                stop_tokens=(TokenType.ANGGEUS, TokenType.TUNGTUNGNA)
            )

        self._expect(TokenType.ANGGEUS,
                     f"Blok 'upami' di baris {tok.line} harus ditutup dengan 'anggeus'")
        self._end_statement()

        return IfNode(condition, then_body, else_body, tok.line)

    def _parse_while(self):
        """while_stmt ::= 'ari' expr NEWLINE statement_list 'anggeus'"""
        tok = self._expect(TokenType.ARI)
        condition = self._parse_expr()
        self._end_statement()
        body = self._parse_statement_list(stop_tokens=(TokenType.ANGGEUS, TokenType.TUNGTUNGNA))
        self._expect(TokenType.ANGGEUS,
                     f"Blok 'ari' di baris {tok.line} harus ditutup dengan 'anggeus'")
        self._end_statement()
        return WhileNode(condition, body, tok.line)

    def _end_statement(self):
        """Statement diakhiri NEWLINE, atau boleh langsung EOF/ANGGEUS/TUNGTUNGNA (baris terakhir)."""
        if self._check(TokenType.NEWLINE):
            self._skip_newlines()
        elif self._check(TokenType.EOF) or self._check(TokenType.ANGGEUS) or self._check(TokenType.TUNGTUNGNA):
            pass
        else:
            tok = self._peek()
            raise ParserError(
                f"Diharapkan akhir baris tapi menemukan '{tok.value}' di baris {tok.line}"
            )

    # ---------- ekspresi (dengan precedence climbing) ----------

    def _parse_expr(self):
        return self._parse_comparison()

    def _parse_comparison(self):
        """comparison ::= additive [ (==|!=|>|<|>=|<=) additive ]"""
        left = self._parse_additive()
        if self._check_any((TokenType.EQ, TokenType.NEQ, TokenType.GT,
                             TokenType.LT, TokenType.GTE, TokenType.LTE)):
            op_tok = self._advance()
            right = self._parse_additive()
            op_map = {
                TokenType.EQ: '==', TokenType.NEQ: '!=', TokenType.GT: '>',
                TokenType.LT: '<', TokenType.GTE: '>=', TokenType.LTE: '<=',
            }
            return BinOpNode(left, op_map[op_tok.type], right, op_tok.line)
        return left

    def _parse_additive(self):
        """additive ::= term { (+|-) term }"""
        node = self._parse_term()
        while self._check_any((TokenType.PLUS, TokenType.MINUS)):
            op_tok = self._advance()
            op = '+' if op_tok.type == TokenType.PLUS else '-'
            right = self._parse_term()
            node = BinOpNode(node, op, right, op_tok.line)
        return node

    def _parse_term(self):
        """term ::= factor { (*|/|%) factor }"""
        node = self._parse_factor()
        while self._check_any((TokenType.STAR, TokenType.SLASH, TokenType.PERSEN)):
            op_tok = self._advance()
            op = {TokenType.STAR: '*', TokenType.SLASH: '/', TokenType.PERSEN: '%'}[op_tok.type]
            right = self._parse_factor()
            node = BinOpNode(node, op, right, op_tok.line)
        return node

    def _parse_factor(self):
        """factor ::= NUMBER | STRING | IDENTIFIER | '(' expr ')' | '-' factor"""
        tok = self._peek()

        if tok.type == TokenType.NUMBER:
            self._advance()
            return NumberNode(tok.value, tok.line)

        if tok.type == TokenType.STRING:
            self._advance()
            return StringNode(tok.value, tok.line)

        if tok.type == TokenType.IDENTIFIER:
            self._advance()
            return VarNode(tok.value, tok.line)

        if tok.type == TokenType.LPAREN:
            self._advance()
            node = self._parse_expr()
            self._expect(TokenType.RPAREN, f"Diharapkan ')' di baris {tok.line}")
            return node

        if tok.type == TokenType.MINUS:
            self._advance()
            operand = self._parse_factor()
            return UnaryOpNode('-', operand, tok.line)

        raise ParserError(
            f"Ekspresi tidak valid: token '{tok.value}' ({tok.type}) di baris {tok.line}"
        )


# ============================================================
# ENTRY POINT (dipanggil dari main.py)
# ============================================================

def parse_to_ast(tokens):
    """Fungsi pembungkus agar kompatibel dengan main.py: terima list token
    dari lexer, kembalikan ProgramNode (root AST)."""
    parser = Parser(tokens)
    return parser.parse_program()
