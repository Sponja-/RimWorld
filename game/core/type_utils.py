from __future__ import annotations

import dataclasses
import inspect
from abc import abstractmethod
from typing import Any, Callable, Generic, TypeVar

from .events import EventfulMeta

DATACLASS_PARAMS = ["eq", "frozen", "init", "order", "repr", "unsafe_hash"]


def get_methods(cls: type) -> list[tuple[str, Callable]]:
    return inspect.getmembers(cls, predicate=inspect.ismethod)


def get_dataclass_params(cls: type) -> dict[str, bool]:
    return {
        paramName: getattr(cls.__dataclass_params__, paramName)
        for paramName in DATACLASS_PARAMS
    }


def get_dataclasses(cls: type) -> set[str]:
    return {
        name for name, value in cls.__dict__.items() if dataclasses.is_dataclass(value)
    }


class DataclassInheritance(EventfulMeta):
    """
    Adds automatic inheritance for nested dataclasses and gives them __slots__
    """

    def __new__(
        metacls: type[DataclassInheritance],
        clsname: str,
        bases: tuple[DataclassInheritance, ...],
        namespace: dict[str, Any],
    ) -> DataclassInheritance:

        dataclass_names = set(
            name for name, value in namespace.items() if dataclasses.is_dataclass(value)
        )

        for base in bases:
            dataclass_names |= get_dataclasses(base)

        for name in dataclass_names:
            cls_dataclass = namespace.get(name, None)
            qualname = getattr(cls_dataclass, "__qualname__", f"{clsname}.{name}")

            fields: list[dataclasses.Field] = []
            methods: list[tuple[str, Callable]] = []

            field_names: set[str] = set()
            method_names: set[str] = set()

            base_params = None

            for base in bases:
                if (base_class := getattr(base, name, None)) is not None:
                    base_fields = dataclasses.fields(base_class)
                    fields.extend(
                        filter(
                            lambda new_field: new_field.name not in field_names,
                            base_fields,
                        )
                    )
                    field_names |= {field.name for field in base_fields}

                    base_methods = get_methods(base_class)
                    methods.extend(
                        filter(
                            lambda new_method: new_method[0] not in method_names,
                            base_methods,
                        )
                    )
                    method_names |= {method[0] for method in base_methods}

                    # Asumes these params are the same for all bases
                    base_params = get_dataclass_params(base_class)

            if cls_dataclass is not None:
                cls_fields = dataclasses.fields(cls_dataclass)
                fields.extend(
                    filter(
                        lambda new_field: not any(
                            new_field.name == existing_field.name
                            for existing_field in fields
                        ),
                        cls_fields,
                    )
                )
                field_names = {field.name for field in cls_fields}

                cls_methods = get_methods(cls_dataclass)
                methods.extend(
                    filter(
                        lambda new_method: not any(
                            new_method[0] == existing_method[0]
                            for existing_method in methods
                        ),
                        cls_methods,
                    )
                )
                method_names |= {method[0] for method in cls_methods}

            params = base_params or get_dataclass_params(cls_dataclass)

            # Can't use bases because they might have __slots__
            unslotted_class = dataclasses.make_dataclass(
                name,
                [(field.name, field.type, field) for field in fields],
                namespace=dict(methods),
                **params,
            )

            # Source: https://github.com/ericvsmith/dataclasses/blob/master/dataclass_tools.py
            slotted_dict = dict(unslotted_class.__dict__)
            slotted_dict["__slots__"] = field_names

            for field_name in field_names:
                slotted_dict.pop(field_name, None)

            slotted_dict.pop("__dict__", None)
            slotted_class = type(unslotted_class)(name, (), slotted_dict)

            slotted_class.__qualname__ = qualname

            namespace[name] = slotted_class

        return super().__new__(metacls, clsname, bases, namespace)


def AbstractProperty() -> property:
    return property(abstractmethod(lambda self: None))
