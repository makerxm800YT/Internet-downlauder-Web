# errors.py
class DownloadError(Exception):
    """Base download error"""
    pass

class URLError(DownloadError):
    """Invalid URL"""
    pass

class SpotifyError(DownloadError):
    """Spotify download failed"""
    pass

class FormatError(DownloadError):
    """Unsupported format"""
    pass
