# src/optimizer.py
"""
CODE OPTIMIZER - SundaLang
============================
Tahap keempat compiler: menyederhanakan AST sebelum code generation,
tanpa mengubah makna/perilaku program (semantics-preserving).

Optimasi yang diimplementasikan:

  1. CONSTANT FOLDING
     Ekspresi yang KEDUA operand-nya berupa literal angka dihitung
     langsung saat compile time. Contoh: `2 + 3 * 4` dilipat menjadi
     literal `14` di dalam AST, sehingga saat runtime Python tidak
     perlu menghitung ulang.

  2. DEAD CODE ELIMINATION (sederhana)
     Blok `upami` (if) yang kondisinya berhasil dilipat (constant
     folding) menjadi nilai boolean yang sudah pasti (misal
     `upami 1 == 1`) akan disederhanakan: hanya cabang yang pasti
     dieksekusi yang dipertahankan, cabang yang mustahil tercapai
     dibuang.

Optimizer ini bekerja secara REKURSIF di seluruh pohon (termasuk masuk
ke dalam tubuh if/else/while), bukan hanya satu lintasan flat seperti
versi sebelumnya.
"""

from parser_ast import (
    ProgramNode, AssignNode, PrintNode, IfNode, WhileNode,
    BinOpNode, UnaryOpNode, NumberNode, StringNode, VarNode,
)

_ARITH_OPS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else None,
    '%': lambda a, b: a % b if b != 0 else None,
}

_COMPARE_OPS = {
    '==': lambda a, b: a == b,
    '!=': lambda a, b: a != b,
    '>':  lambda a, b: a > b,
    '<':  lambda a, b: a < b,
    '>=': lambda a, b: a >= b,
    '<=': lambda a, b: a <= b,
}


class Optimizer:
    def __init__(self):
        self.fold_count = 0
        self.dead_branch_count = 0

    # ---------- entry point ----------

    def optimize(self, program_node: ProgramNode) -> ProgramNode:
        new_statements = self._optimize_statements(program_node.statements)
        return ProgramNode(new_statements)

    # ---------- statement level ----------

    def _optimize_statements(self, statements):
        result = []
        for stmt in statements:
            optimized = self._optimize_statement(stmt)
            # _optimize_statement bisa mengembalikan None (statement dibuang)
            # atau list (hasil inlining dead-code-elimination pada if)
            if optimized is None:
                continue
            if isinstance(optimized, list):
                result.extend(optimized)
            else:
                result.append(optimized)
        return result

    def _optimize_statement(self, node):
        if isinstance(node, AssignNode):
            node.expr = self._fold(node.expr)
            return node

        if isinstance(node, PrintNode):
            node.expr_list = [self._fold(e) for e in node.expr_list]
            return node

        if isinstance(node, IfNode):
            node.condition = self._fold(node.condition)
            node.then_body = self._optimize_statements(node.then_body)
            if node.else_body is not None:
                node.else_body = self._optimize_statements(node.else_body)

            # Dead code elimination: jika kondisi sudah pasti True/False
            # (hasil constant folding berupa NumberNode 1/0 dari boolean
            # Python), kita bisa langsung pilih cabang yang relevan saja.
            if isinstance(node.condition, NumberNode):
                self.dead_branch_count += 1
                if node.condition.value:  # kondisi pasti benar
                    print(f"  -> [OPTIMASI] Baris {node.line}: kondisi 'upami' selalu benar, "
                          f"cabang 'lamun_hente' dibuang.")
                    return node.then_body  # inline isi then, buang else
                else:  # kondisi pasti salah
                    print(f"  -> [OPTIMASI] Baris {node.line}: kondisi 'upami' selalu salah, "
                          f"cabang 'upami' dibuang.")
                    return node.else_body if node.else_body is not None else []
            return node

        if isinstance(node, WhileNode):
            node.condition = self._fold(node.condition)
            node.body = self._optimize_statements(node.body)
            return node

        return node

    # ---------- expression level: constant folding ----------

    def _fold(self, node):
        if isinstance(node, (NumberNode, StringNode, VarNode)):
            return node

        if isinstance(node, UnaryOpNode):
            node.operand = self._fold(node.operand)
            if isinstance(node.operand, NumberNode) and node.op == '-':
                self.fold_count += 1
                return NumberNode(-node.operand.value, node.line)
            return node

        if isinstance(node, BinOpNode):
            node.left = self._fold(node.left)
            node.right = self._fold(node.right)

            if isinstance(node.left, NumberNode) and isinstance(node.right, NumberNode):
                a, b = node.left.value, node.right.value
                if node.op in _ARITH_OPS:
                    value = _ARITH_OPS[node.op](a, b)
                    if value is not None:  # None = pembagian nol, jangan dilipat
                        self.fold_count += 1
                        print(f"  -> [OPTIMASI] Baris {node.line}: melipat konstanta "
                              f"{a} {node.op} {b} -> {value}")
                        return NumberNode(value, node.line)
                elif node.op in _COMPARE_OPS:
                    value = _COMPARE_OPS[node.op](a, b)
                    self.fold_count += 1
                    print(f"  -> [OPTIMASI] Baris {node.line}: melipat konstanta "
                          f"{a} {node.op} {b} -> {value}")
                    return NumberNode(1 if value else 0, node.line)
            return node

        return node


def optimize_code(ast):
    """Entry point dipanggil dari main.py, kompatibel dengan nama lama."""
    optimizer = Optimizer()
    return optimizer.optimize(ast)
