import warnings


class ResurfaceWarning(UserWarning):
    def __init__(self, warning_type, environment_var=None, required_type=None):
        self.warning_type = warning_type
        self.env_var = environment_var
        self.required_type = required_type

    def __str__(self):
        if self.warning_type == "argtype":
            warn = (
                f"Invalid type for {self.env_var} "
                + f"(argument should be a {self.required_type}). "
                + "Logger won't be enabled."
            )
        elif self.warning_type == "nologger":
            warn = "Logger is not enabled."
        return warn

    def warn(self):
        warnings.warn(self, stacklevel=2)
