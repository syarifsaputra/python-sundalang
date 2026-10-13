# src/codegen.py
"""
CODE GENERATOR - SundaLang -> Python
=======================================
Tahap kelima (terakhir) compiler: mengubah AST yang sudah dioptimasi
menjadi kode Python yang valid (target code), yang kemudian dieksekusi
oleh `main.py`.

PERBAIKAN PENTING dibanding versi sebelumnya:
Versi sebelumnya mengelola indentasi dengan SATU counter global
(`indent_level`) yang di-increment/decrement berdasarkan tipe baris
SAAT ITU, tanpa mengetahui struktur blok yang sesungguhnya. Akibatnya
baris 'lamun_hente' (else) ikut ter-indent karena urutan operasinya
salah:

    if nilai >= 75:
        print("Lulus")
        else:              # BUG: harusnya sejajar dengan 'if'
        print("Teu Lulus")

Codegen versi ini tidak memakai counter global sama sekali. Sebagai
gantinya, setiap fungsi `_gen_xxx` menerima parameter `indent` (level
saat ini) dan mengembalikan baris-baris kode HANYA pada level itu;
setiap kali turun ke dalam sebuah blok (then_body, else_body, body
while), fungsi childnya dipanggil dengan `indent + 1`. Ini meniru
cara compiler asli melakukan code generation dari struktur pohon,
bukan dari urutan baris linear.
"""

from parser_ast import (
    ProgramNode, AssignNode, PrintNode, IfNode, WhileNode,
    BinOpNode, UnaryOpNode, NumberNode, StringNode, VarNode,
)

INDENT_UNIT = "    "


class CodeGenError(Exception):
    pass


class CodeGenerator:
    def __init__(self):
        self.lines = []

    # ---------- entry point ----------

    def generate(self, program_node: ProgramNode) -> str:
        self.lines = []
        self._gen_statements(program_node.statements, indent=0)
        if not self.lines:
            self.lines.append("pass")  # program kosong tetap valid secara Python
        return "\n".join(self.lines)

    # ---------- statement level ----------

    def _gen_statements(self, statements, indent):
        if not statements:
            self._emit("pass", indent)
            return
        for stmt in statements:
            self._gen_statement(stmt, indent)

    def _gen_statement(self, node, indent):
        if isinstance(node, AssignNode):
            expr_code = self._gen_expr(node.expr)
            self._emit(f"{node.var_name} = {expr_code}", indent)

        elif isinstance(node, PrintNode):
            args = ", ".join(self._gen_expr(e) for e in node.expr_list)
            self._emit(f"print({args})", indent)

        elif isinstance(node, IfNode):
            cond_code = self._gen_expr(node.condition)
            self._emit(f"if {cond_code}:", indent)
            self._gen_statements(node.then_body, indent + 1)
            if node.else_body is not None:
                self._emit("else:", indent)            # sejajar dengan 'if', BUKAN indent+1
                self._gen_statements(node.else_body, indent + 1)

        elif isinstance(node, WhileNode):
            cond_code = self._gen_expr(node.condition)
            self._emit(f"while {cond_code}:", indent)
            self._gen_statements(node.body, indent + 1)

        else:
            raise CodeGenError(f"Node statement tidak dikenal saat code generation: {node!r}")

    def _emit(self, code_line, indent):
        self.lines.append(f"{INDENT_UNIT * indent}{code_line}")

    # ---------- expression level ----------

    def _gen_expr(self, node):
        if isinstance(node, NumberNode):
            return repr(node.value)

        if isinstance(node, StringNode):
            return repr(node.value)

        if isinstance(node, VarNode):
            return node.name

        if isinstance(node, UnaryOpNode):
            return f"({node.op}{self._gen_expr(node.operand)})"

        if isinstance(node, BinOpNode):
            left_code = self._gen_expr(node.left)
            right_code = self._gen_expr(node.right)
            return f"({left_code} {node.op} {right_code})"

        raise CodeGenError(f"Node ekspresi tidak dikenal saat code generation: {node!r}")


def generate_code(ast):
    """Entry point dipanggil dari main.py, kompatibel dengan nama lama."""
    generator = CodeGenerator()
    return generator.generate(ast)
