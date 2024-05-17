import os
from distutils.util import strtobool


class ConfigError(Exception):
    pass


class RequiredNotProvided(Exception):
    pass


class ConfigField:
    def __init__(self, processor=str, default=None, required=False, from_var=None):
        self.processor = processor
        self.default = default
        self.required = required
        self.from_var = from_var

        self.name = None

    @property
    def env_var(self):
        return self.from_var or self.name

    def validate(self, value):
        if value is None and self.required:
            raise RequiredNotProvided()

    def load(self, value):
        if value:
            value = self.processor(value)
        elif self.default is not None:
            if callable(self.default):
                value = self.default()
            else:
                value = self.default
        return value


class IntConfig(ConfigField):
    def __init__(self, **kwargs):
        super().__init__(processor=int, **kwargs)


class FloatConfig(ConfigField):
    def __init__(self, **kwargs):
        super().__init__(processor=float, **kwargs)


class BooleanConfig(ConfigField):
    def __init__(self, **kwargs):
        super().__init__(processor=strtobool, **kwargs)


class EnvironConfigurationMeta(type):
    def __call__(cls, *args, **kwargs):
        raise TypeError("Can't instance a configuration class")

    def __init__(cls, name, bases, dct):
        super(EnvironConfigurationMeta, cls).__init__(name, bases, dct)

        base_config_fields = []
        for base in bases:
            base_config_fields += base._config_fields
        cls._config_fields = base_config_fields
        for k, field in dct.items():
            if isinstance(field, ConfigField):
                field.name = k
                config_val = os.environ.get(field.env_var)
                try:
                    field.validate(config_val)
                except RequiredNotProvided:
                    raise ConfigError(f'{cls.__name__}.{field.name} '
                                      f'(from env {field.env_var})'
                                      f' is required, but not provided')
                config_val = field.load(config_val)
                cls._config_fields.append(k)
                setattr(cls, k, config_val)

    def __getitem__(cls, item):
        return getattr(cls, item)


class BaseEnvironConfig(metaclass=EnvironConfigurationMeta):
    """Base config class.
    Loads all config params that are instances of ConfigField from environ,
    applies preprocessor, validates if required.

    Example:
    ```
    >>> class Config(BaseEnvironConfig):
    ...  DEBUG = ConfigField(processor=strtobool, default=True)
    ...
    >>> Config.DEBUG
    True
    ```

    Loads env var "DEBUG", applies function `string_to_bool` to the returned value,
    if the result is None uses default of True.

    Since its a global class it's __VERY IMPORTANT__ to import it like this:

    ```
    from package import module
    print(module.ConfigClass.as_text())
    ```

    and __not__ like this:

    ```
    from package.module import ConfigClass
    print(ConfigClass.as_text())
    ```

    The first variant allows you to monkey patch the config during testing.
    Pytest example:

    ```
    from package.module import ConfigClass

    class TestConfig(ConfigClass):
        pass

    TestConfig.TEST = True

    monkeypatch.setattr('package.module.ConfigClass', TestConfig)
    ```

    After this all code accesing `module.ConfigClass` will get `TestConfig`.
    """

    @classmethod
    def _filter_attrs(cls, include_private, exclude):
        attrs = [(k, getattr(cls, k)) for k in cls._config_fields if
                 not callable(getattr(cls, k))]
        if not include_private:
            attrs = filter(lambda p: not p[0].startswith('_'), attrs)
        if exclude:
            attrs = filter(lambda p: p[0] in exclude, attrs)
        return attrs

    @classmethod
    def as_dict(cls, include_private=False, exclude=None, censor=None):
        if not exclude:
            exclude = []
        if not censor:
            censor = []
        attrs = dict(cls._filter_attrs(include_private, exclude=exclude))
        for censored in censor:
            if attrs.get(censored):
                attrs[censored] = '*' * len(attrs[censored])
        return attrs

    @classmethod
    def as_text(cls, include_private=False, exclude=None, censor=None):
        data_fields = cls.as_dict(include_private, exclude=exclude, censor=censor)
        attrs = [
            "{}={}".format(k, str(v)) for k, v in data_fields.items()]
        attr_list = "\n\t".join(attrs)
        return f'{cls.__name__}:\n\t{attr_list}'
