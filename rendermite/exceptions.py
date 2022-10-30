class RendermiteError(Exception):
    """Base exception for all errors raised by rendermite"""

    def __init__(self, *args: object) -> None:
        super().__init__(self.__class__.__doc__, *args)

class LoaderError(RendermiteError):
    """Base exception for all errors raised by the model loading process"""

class OrphanModelError(LoaderError):
    """Model inherits from a nonexistent parent"""

class MissingDisplayError(RendermiteError):
    """The item could not be rendered as it is missing the required ``ModelDisplay``"""

class UnsupportedBuiltinError(RendermiteError):
    """This model inherits from an unsupported builtin`"""

class FetchAssetsError(RendermiteError):
    """Base exception for all errors raised by the asset fetching process"""

class InvalidVersionError(FetchAssetsError):
    """The requested version package could not be found"""
