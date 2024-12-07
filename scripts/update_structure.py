import os

def generate_structure(start_path='.', indent='    '):
    """
    Genera la rappresentazione della struttura di directory e file del repository.
    """
    output = []
    for root, dirs, files in os.walk(start_path):
        # Remove hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv']
        level = root.replace(start_path, '').count(os.sep)
        indent_level = indent * level
        output.append(f"{indent_level}├── {os.path.basename(root)}/")
        for f in files:
            if not f.startswith('.'):
                output.append(f"{indent_level}{indent}{f}")
    return '\n'.join(output)

def update_readme_structure(readme_file='README.md', start_path='.'):
    """
    Aggiorna il contenuto della sezione 'Struttura del Repository' in README.md.
    """
    structure = generate_structure(start_path=start_path)
    try:
        with open(readme_file, 'r') as file:
            content = file.readlines()
        
        start_marker = "<!-- START STRUCTURE -->"
        end_marker = "<!-- END STRUCTURE -->"
        start_index = next(i for i, line in enumerate(content) if start_marker in line) + 1
        end_index = next(i for i, line in enumerate(content) if end_marker in line)
        
        # Update the content between start and end marker
        content[start_index:end_index] = [structure + '\n']
        
        with open(readme_file, 'w') as file:
            file.writelines(content)
        
        print("README.md aggiornato con la nuova struttura del repository.")
    except Exception as e:
        print(f"Errore durante l'aggiornamento di README.md: {e}")

if __name__ == "__main__":
    update_readme_structure()
