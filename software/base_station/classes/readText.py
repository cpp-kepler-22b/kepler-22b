class TextFileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_content = None  # Variable to store file content as a string

    def read_file(self):
        try:
            with open(self.file_path, 'r') as file:
                self.file_content = file.read()
            print("File content successfully read.")
        except FileNotFoundError:
            print("File not found. Please check the file path.")
            self.file_content = None
        except Exception as e:
            print(f"An error occurred: {e}")
            self.file_content = None

    def get_content(self):
        return self.file_content
