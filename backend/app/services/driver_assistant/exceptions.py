class DriverAssistantError(Exception):
    """خطای پایه دستیار راننده."""


class SessionNotFoundException(DriverAssistantError):
    """جلسه راننده پیدا نشد."""


class DestinationNotFoundException(DriverAssistantError):
    """مقصد پیدا نشد."""


class AmbiguousDestinationException(DriverAssistantError):
    """مقصد چندمعنایی است."""


class OSRMErrorException(DriverAssistantError):
    """خطای سرویس OSRM."""


class KernelErrorException(DriverAssistantError):
    """خطای HDP Kernel."""


class GPSValidationException(DriverAssistantError):
    """مختصات GPS نامعتبر است."""


# Backward-compatible alias used by navigation/POI services.
DestinationNotFoundError = DestinationNotFoundException
