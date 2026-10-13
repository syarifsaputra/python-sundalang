# src/semantic.py
from parser_ast import (
    ProgramNode, AssignNode, PrintNode, IfNode, WhileNode,
    BinOpNode, UnaryOpNode, NumberNode, StringNode, VarNode,
)


class SemanticError(Exception):
    pass


class SymbolTable:
    """Tabel simbol sederhana: nama variabel -> tipe data yang terakhir
    diketahui ('angka', 'teks', atau 'tidak diketahui')."""

    def __init__(self):
        self._table = {}

    def declare(self, name, var_type):
        self._table[name] = var_type

    def is_declared(self, name):
        return name in self._table

    def get_type(self, name):
        return self._table.get(name, 'tidak diketahui')

    def as_dict(self):
        return dict(self._table)

    def __repr__(self):
        return repr(self._table)


def _infer_type(node, symtab):
    """Coba tebak tipe ekspresi untuk disimpan di tabel simbol."""
    if isinstance(node, NumberNode):
        return 'angka'
    if isinstance(node, StringNode):
        return 'teks'
    if isinstance(node, VarNode):
        return symtab.get_type(node.name)
    if isinstance(node, BinOpNode):
        left_t = _infer_type(node.left, symtab)
        right_t = _infer_type(node.right, symtab)
        if node.op in ('==', '!=', '>', '<', '>=', '<='):
            return 'boolean'
        if left_t == 'angka' and right_t == 'angka':
            return 'angka'
        return 'tidak diketahui'
    if isinstance(node, UnaryOpNode):
        return _infer_type(node.operand, symtab)
    return 'tidak diketahui'


class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.errors = []

    def analyze(self, program_node: ProgramNode):
        self._visit_statements(program_node.statements)
        return self.symtab, self.errors

    # ---------- statement visitors ----------

    def _visit_statements(self, statements):
        for stmt in statements:
            self._visit_statement(stmt)

    def _visit_statement(self, node):
        if isinstance(node, AssignNode):
            self._visit_assign(node)
        elif isinstance(node, PrintNode):
            self._visit_print(node)
        elif isinstance(node, IfNode):
            self._visit_if(node)
        elif isinstance(node, WhileNode):
            self._visit_while(node)
        else:
            raise SemanticError(f"Node statement tidak dikenal: {node!r}")

    def _visit_assign(self, node: AssignNode):
        self._visit_expr(node.expr)          # variabel di sisi kanan harus valid dulu
        var_type = _infer_type(node.expr, self.symtab)
        self.symtab.declare(node.var_name, var_type)

    def _visit_print(self, node: PrintNode):
        for expr in node.expr_list:
            self._visit_expr(expr)

    def _visit_if(self, node: IfNode):
        self._visit_expr(node.condition)
        self._visit_statements(node.then_body)
        if node.else_body is not None:
            self._visit_statements(node.else_body)

    def _visit_while(self, node: WhileNode):
        self._visit_expr(node.condition)
        self._visit_statements(node.body)

    # ---------- expression visitors ----------

    def _visit_expr(self, node):
        if isinstance(node, VarNode):
            if not self.symtab.is_declared(node.name):
                msg = (f"[SEMANTIC ERROR] Baris {node.line}: Variabel '{node.name}' "
                       f"teu acan dideklarasikeun (belum dibuat)!")
                self.errors.append(msg)
        elif isinstance(node, BinOpNode):
            self._visit_expr(node.left)
            self._visit_expr(node.right)
        elif isinstance(node, UnaryOpNode):
            self._visit_expr(node.operand)
        elif isinstance(node, (NumberNode, StringNode)):
            pass  # literal selalu valid
        else:
            raise SemanticError(f"Node ekspresi tidak dikenal: {node!r}")


def semantic_analysis(ast):
    """Entry point dipanggil dari main.py. Mengembalikan dict tabel
    simbol agar antarmuka lama tetap kompatibel, dan mencetak error
    semantik (jika ada) seperti versi sebelumnya."""
    analyzer = SemanticAnalyzer()
    symtab, errors = analyzer.analyze(ast)
    for err in errors:
        print(err)
    return symtab.as_dict()
