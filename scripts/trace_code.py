
import os

def collect_specific_files(file_paths, output_file):
    """
    Raccoglie il contenuto dei file specificati e lo salva in un file di output.
    """
    with open(output_file, 'w', encoding='utf-8') as out_file:
        out_file.write('"""\nCode Collection for Specific Files\n"""\n\n')
        
        for file_path in file_paths:
            if not os.path.isfile(file_path):
                print(f"Skipping {file_path}: Not a valid file.")
                continue

            relative_path = os.path.relpath(file_path)
            
            # Filtra file binari o con permessi non accessibili
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except (UnicodeDecodeError, PermissionError):
                print(f"Skipping file {relative_path} due to encoding/permission issues.")
                continue
            
            # Scrivi il nome del file e il contenuto
            out_file.write(f'# File: {relative_path}\n')
            out_file.write(f'# Lines: {len(lines)}\n')
            out_file.write(''.join(lines))
            out_file.write('\n' + '='*40 + '\n\n')  # Delimitatore tra file

    print(f"Code collected and saved to {output_file}.")


if __name__ == "__main__":
    # Elenco dei file specifici da raccogliere
    file_paths = [
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/models/requests.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/models/responses.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/services/groq.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/services/news_retrieval.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/services/vectara.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/utils/image_generation.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/utils/llm.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/utils/meme_generation.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/utils/openai_client.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/utils/video_generation.py",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/main.py",
        # "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/backend/Makefile",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/app/layout.tsx",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/app/page.tsx",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/components/content-generator.tsx",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/styles/globals.css",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/next-env.d.ts",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/frontend/tsconfig.json",
        "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/README.md"
    ]

    # File di output
    output_file_path = "/Users/stefanobisignano/Desktop/Personal/App/PostGenius/scripts/collected_specific_code.txt"

    # Raccogli il codice e salva nel file di output
    collect_specific_files(file_paths, output_file_path)
