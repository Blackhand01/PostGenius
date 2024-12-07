import os

def create_test_files():
    # Base directory for tests
    test_dir = "tests"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)

    # Scan the 'src' directory for modules
    src_dir = "src"
    if not os.path.exists(src_dir):
        print(f"Source directory '{src_dir}' not found. No tests created.")
        return

    # Create a test file for each module
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.relpath(root, src_dir)
                module_name = file.replace(".py", "")
                test_file_name = f"test_{module_name}.py"
                test_file_path = os.path.join(test_dir, test_file_name)

                # Create boilerplate test file
                if not os.path.exists(test_file_path):
                    with open(test_file_path, "w") as f:
                        f.write(f"""import unittest\nfrom src.{module_path.replace('/', '.')} import {module_name}\n\n\n""")
                        f.write(f"""class Test{module_name.capitalize()}(unittest.TestCase):\n""")
                        f.write(f"    def test_placeholder(self):\n")
                        f.write(f"        # Add your tests here\n")
                        f.write(f"        self.assertTrue(True)\n\n")
                        f.write("if __name__ == '__main__':\n")
                        f.write("    unittest.main()\n")
                    print(f"Created test file: {test_file_path}")
                else:
                    print(f"Test file already exists: {test_file_path}")

if __name__ == "__main__":
    create_test_files()
