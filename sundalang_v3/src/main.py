# src/main.py
import sys
import os

# Import semua fase compiler dari file masing-masing
from lexer import tokenize, LexerError
from parser_ast import parse_to_ast, ParserError
from semantic import semantic_analysis
from optimizer import optimize_code
from codegen import generate_code, CodeGenError


def run_compiler(show_tokens=False, show_generated=False):
    print("=============================================")
    print(" SUNDALANG COMPILER - PROSES KOMPILASI SUNDA")
    print("=============================================\n")

    if len(sys.argv) < 2:
        file_path = input("Asupken file .sunda: ")
    else:
        file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"[ERROR] File '{file_path}' eweh filena te di temukan!")
        return

    # Membaca kode
    with open(file_path, 'r', encoding='utf-8') as f:
        sunda_code = f.read()

    # ---------- [1] LEXICAL ANALYSIS ----------
    print("[1] Lexical Analysis (Tokenisasi) berjalan...")
    try:
        tokens = tokenize(sunda_code)
    except LexerError as e:
        print(f"[LEXER ERROR] {e}")
        return
    print(f"    {len(tokens)} token dihasilkan.")
    if show_tokens:
        for t in tokens:
            print(f"    {t}")

    # ---------- [2] PARSING -> AST ----------
    print("\n[2] Parsing ke AST (Abstract Syntax Tree)...")
    try:
        ast = parse_to_ast(tokens)
    except ParserError as e:
        print(f"[PARSER ERROR] {e}")
        return
    print(f"    Berhasil membentuk AST dengan {len(ast.statements)} statement top-level.")

    # ---------- [3] SEMANTIC ANALYSIS ----------
    print("\n[3] Semantic Analysis & Tabel Simbol...")
    sym_table = semantic_analysis(ast)
    print(f"    Tabel Simbol: {sym_table}")

    # ---------- [4] CODE OPTIMIZATION ----------
    print("\n[4] Code Optimization...")
    opt_ast = optimize_code(ast)

    # ---------- [5] CODE GENERATION ----------
    print("\n[5] Code Generation...")
    try:
        target_code = generate_code(opt_ast)
    except CodeGenError as e:
        print(f"[CODEGEN ERROR] {e}")
        return

    if show_generated:
        print("\n--------- Kode Python hasil generate ---------")
        print(target_code)
        print("-----------------------------------------------")

    # ---------- EKSEKUSI HASIL ----------
    print("\n=============================================")
    print(" HASIL OUTPUT NA PROGRAM SUNDALANG")
    print("=============================================")
    try:
        exec(target_code, {})
    except Exception as e:
        print(f"Eror saat eksekusi: {e}")
    print("=============================================\n")


if __name__ == "__main__":
    debug_tokens = '--tokens' in sys.argv
    debug_gen = '--show-gen' in sys.argv
    sys.argv = [a for a in sys.argv if a not in ('--tokens', '--show-gen')]
    run_compiler(show_tokens=debug_tokens, show_generated=debug_gen)