from .entities import Function

class Index(dict):
    def add_function(self, name, rewrite: bool = False):
        def decorator(fn):
            entity = Function.make(name)(fn)
            self.add_value(name, entity, rewrite=rewrite)
            return entity
        return decorator

    def add_value(self, name, value, rewrite: bool = False):
        if name in self and not rewrite:
            raise LookupError(f"{name} is already present")
        self[name] = value