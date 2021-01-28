from .tcx_loader import TcxLoader


class Loader:
    def __init__(self, filename):
        self.filename = filename

    def get_loader(self, file_content):
        ending = self.filename.split(".")[-1]
        if ending.lower() in ["tcx", "xml"]:
            return TcxLoader(file_content)
        else:
            raise ValueError("Cannot handle file format '%s'" % ending)
