class GubkinAPIError(Exception):
    pass


class ParsingError(GubkinAPIError):
    pass


class GubkinConnectionError(GubkinAPIError):
    pass
