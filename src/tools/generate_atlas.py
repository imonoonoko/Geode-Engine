
import os
import ast
import inspect
import importlib.util
from datetime import datetime

# Target Directories
SRC_DIR = "src"
OUTPUT_FILE = os.path.join("docs", "FUNCTION_ATLAS.md")

def get_function_signature(node):
    """
    Reconstruct function signature/arguments from AST node.
    """
    args = []
    defaults = dict()
    
    # Defaults are for the last n arguments
    if node.args.defaults:
        for i, default in enumerate(reversed(node.args.defaults)):
            arg_name = node.args.args[-1 - i].arg
            # Try to get simple default representation
            if isinstance(default, ast.Constant):
                defaults[arg_name] = repr(default.value)
            else:
                defaults[arg_name] = "..." # Complex default
                
    for arg in node.args.args:
        a = arg.arg
        if node.args.defaults and arg.arg in defaults:
            a += f"={defaults[arg.arg]}"
        args.append(a)
        
    if node.args.vararg:
        args.append(f"*{node.args.vararg.arg}")
    if node.args.kwarg:
        args.append(f"**{node.args.kwarg.arg}")
        
    return f"({', '.join(args)})"

def parse_file(filepath):
    """
    Parse a python file and return structure.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())
        
    structure = []
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_info = {
                "type": "class",
                "name": node.name,
                "doc": ast.get_docstring(node),
                "methods": []
            }
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_doc = ast.get_docstring(item)
                    sig = get_function_signature(item)
                    class_info["methods"].append({
                        "name": item.name,
                        "signature": sig,
                        "doc": method_doc
                    })
            structure.append(class_info)
            
        elif isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node)
            sig = get_function_signature(node)
            structure.append({
                "type": "function",
                "name": node.name,
                "signature": sig,
                "doc": func_doc
            })
            
    return structure

def generate_atlas():
    """
    Main Generation Loop
    """
    print(f"🗺️ Generating Atlas from {SRC_DIR}...")
    
    lines = []
    lines.append(f"# 🗺️ 機能アトラス (FUNCTION ATLAS)")
    lines.append(f"> **生成日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **ソース**: `{SRC_DIR}/`")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Walk through directories
    for root, dirs, files in os.walk(SRC_DIR):
        py_files = [f for f in files if f.endswith(".py") and f != "__init__.py"]
        
        if not py_files:
            continue
            
        # Section Header (Directory)
        rel_dir = os.path.relpath(root, ".")
        lines.append(f"## 📁 `{rel_dir}`")
        
        for file in py_files:
            filepath = os.path.join(root, file)
            print(f"  Parsing {file}...")
            
            lines.append(f"### 📄 `{file}`")
            
            try:
                items = parse_file(filepath)
                if not items:
                    lines.append("*公開定義が見つかりません。*")
                    lines.append("")
                    continue
                
                for item in items:
                    if item["type"] == "class":
                        doc = item["doc"].strip().split('\n')[0] if item["doc"] else ""
                        lines.append(f"- **class {item['name']}**")
                        if doc: lines.append(f"  - 📝 *{doc}*")
                        
                        for method in item["methods"]:
                            if method["name"].startswith("_") and method["name"] != "__init__":
                                continue # Skip private methods for atlas (unless important?)
                            
                            mdoc = method["doc"].strip().split('\n')[0] if method["doc"] else ""
                            lines.append(f"  - `def {method['name']}{method['signature']}`")
                    
                    elif item["type"] == "function":
                        doc = item["doc"].strip().split('\n')[0] if item["doc"] else ""
                        lines.append(f"- **def {item['name']}{item['signature']}**")
                        if doc: lines.append(f"  - 📝 *{doc}*")
            
                lines.append("")
            except Exception as e:
                lines.append(f"⚠️ *Parse Error: {e}*")
                lines.append("")

    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    print(f"✅ Atlas Generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_atlas()
