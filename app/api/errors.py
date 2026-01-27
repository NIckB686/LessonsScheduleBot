class GubkinAPIError(Exception):
    pass


class GubkinParsingError(GubkinAPIError):
    pass


class GubkinConnectionError(GubkinAPIError):
    pass


class GubkinRegisterError(GubkinAPIError):
    pass
