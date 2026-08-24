class BandariEngineError(Exception):
    code = "bandari_error"
    def to_dict(self):
        return {"code": self.code, "error": str(self)}

class BandariEngineDisabledError(BandariEngineError):
    code = "bandari_disabled"

class BandariEngineUnavailableError(BandariEngineError):
    code = "bandari_unavailable"

class BandariEngineTimeoutError(BandariEngineError):
    code = "bandari_timeout"

class BandariEngineHTTPError(BandariEngineError):
    code = "bandari_http_error"

class BandariEngineInvalidResponseError(BandariEngineError):
    code = "bandari_invalid_response"
