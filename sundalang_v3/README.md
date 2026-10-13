# SundaLang (Python to Sundanese Language)

SundaLang is a custom, localized programming language built with Python. It uses a custom lexer and parser to interpret and execute code written using Sundanese language syntax and logic.

## 📂 Project Structure

- `src/` - Contains the core components of the language:
  - `lexer.py` - Tokenizes the Sundanese source code.
  - `parser_ast.py` - Builds the Abstract Syntax Tree (AST).
  - `semantic.py` - Performs semantic analysis.
  - `codegen.py` - Handles code generation.
  - `optimizer.py` - Optimizes the generated code.
  - `main.py` - The entry point to run the language interpreter.
- `CHANGELOG_v3.md` - Version history and updates for version 3.
- `*.txt` - Sample SundaLang source code files (`contoh_kondisi.txt`, `hitungsunda.txt`, `testnilailulus.txt`, `testsunda.txt`).

## 🛠️ Prerequisites

To run this project, you need to have Python installed on your machine (Python 3.x or higher).

## 🚀 How to Try and Run SundaLang

### 1. Clone the Repository

First, clone this repository to your local machine:

```bash
git clone [https://github.com/syarifsaputra/python-sundalang.git](https://github.com/syarifsaputra/python-sundalang.git)

```

Navigate to the project directory (make sure you are inside the folder containing the src folder):

Bash
cd python-sundalang/sundalang_v3 2. How to Run the Code
To execute a SundaLang script, use Python to run the main.py file inside the src/ directory and pass your .txt file as an argument:

Bash
python src/main.py <filename>.txt 3. Try the Examples
I have provided several .txt files in this repository to demonstrate how the language works. You can test them by running the following commands in your terminal:

Run the General Syntax Test:

Bash
python src/main.py testsunda.txt
Run the Mathematical Operations Example:

Bash
python src/main.py hitungsunda.txt
Run the Conditionals (If-Else) Example:

Bash
python src/main.py contoh_kondisi.txt
Run the Passing Grade Logic Example:

Bash
python src/main.py testnilailulus.txt
📝 Writing Your Own Code
You can create your own .txt file in the root directory, write your logic using Sundanese syntax, and run it using the same python src/main.py yourfile.txt command!

📜 License
This project is open-source and created for educational purposes.
