"""Type analysis utilities for RDFantic field introspection."""

from __future__ import annotations

import types
from collections.abc import Sequence
from typing import Annotated, Any, NamedTuple, Union, get_args, get_origin


class TypeInfo(NamedTuple):
    """Type information for a field: whether it is a list and its item type."""

    is_list: bool
    item_type: object
    is_union: bool = False
    contains_none: bool = False


class TypeAnalyzer:
    """Static utility class for analyzing Python type annotations.

    Provides methods to unwrap complex type annotations like Annotated, Union,
    Optional, and Sequence types to extract the underlying item types.
    """

    @staticmethod
    def _is_sequence_type(annotation: Any) -> bool:
        """Check if an annotation is a Sequence type (list, tuple, etc.) but not str."""
        origin = get_origin(annotation)
        return (
            origin is not None
            and isinstance(origin, type)
            and issubclass(origin, Sequence)
            and not issubclass(origin, str)
        )

    @staticmethod
    def contains_nested_list(annotation: Any, depth: int = 0) -> bool:  # noqa: PLR0911
        """Recursively check if an annotation contains a nested list.

        Parameters
        ----------
        annotation : Any
            The type annotation to check.
        depth : int
            Current nesting depth of list types.

        Returns
        -------
        bool
            True if the annotation contains a nested list (list inside list).
        """
        # Unwrap Annotated
        if get_origin(annotation) is type(None):
            return False

        # Handle Annotated[T, ...]
        if get_origin(annotation) is Annotated:
            inner_type = get_args(annotation)[0]
            return TypeAnalyzer.contains_nested_list(inner_type, depth)

        if get_origin(annotation) is types.UnionType or str(get_origin(annotation)) == "typing.Union":
            args = get_args(annotation)
            for arg in args:
                if arg is type(None):
                    continue
                if TypeAnalyzer.contains_nested_list(arg, depth):
                    return True
            return False

        # Check if this is a sequence type
        if TypeAnalyzer._is_sequence_type(annotation):
            if depth > 0:
                # We're already inside a list, so this is a nested list
                return True
            # Check the item type(s) of the sequence
            args = get_args(annotation)
            if args:
                for arg in args:
                    if TypeAnalyzer.contains_nested_list(arg, depth + 1):
                        return True

        return False

    @staticmethod
    def get_annotated_type(annotation: Any) -> Any | None:
        """Return the type wrapped by Annotated, or None if not Annotated.

        Args:
            annotation: The type annotation to inspect.

        Returns
        -------
            The type wrapped by Annotated, or None if not Annotated.
        """
        if get_origin(annotation) is Annotated:
            return get_args(annotation)[0]
        return None

    @staticmethod
    def get_union_types(annotation: Any) -> set[Any]:
        """Return the set of all types in a Union/Optional annotation, or an empty set.

        Args:
            annotation: The type annotation to inspect.

        Returns
        -------
            All types in the Union, or an empty set if not a Union.
        """
        union_types = set()
        if get_origin(annotation) is Union or get_origin(annotation) is types.UnionType:
            union_types = set(get_args(annotation))
            return union_types
        return union_types

    @staticmethod
    def get_union_type(annotation: Any) -> Any | None:
        """Return the first non-None type in a Union/Optional annotation, or None.

        Args:
            annotation: The type annotation to inspect.

        Returns
        -------
            The first non-None type in the Union, or None if not a Union.
        """
        union_types = TypeAnalyzer.get_union_types(annotation)
        if union_types:
            # Return the first non-None type in a stable order (sorted by name)
            non_none = [arg for arg in union_types if arg is not type(None)]
            return next(iter(sorted(non_none, key=lambda t: getattr(t, "__name__", str(t)))), None)
        return None

    @staticmethod
    def get_sequence_type(annotation: Any) -> Any | None:
        """Return the item type if annotation is a Sequence (not str), else None.

        Args:
            annotation: The type annotation to inspect.

        Returns
        -------
            The item type if annotation is a Sequence (not str), else None.
        """
        origin = get_origin(annotation)
        if origin and isinstance(origin, type) and issubclass(origin, Sequence) and not issubclass(origin, str):
            return get_args(annotation)[0]
        return None

    @staticmethod
    def base_model_or_str(item_type: types.UnionType | type) -> tuple[bool, bool]:
        """Check if a type is RdfanticBaseModel, str, or a Union of both.

        Parameters
        ----------
        item_type : types.UnionType | type
            The type to analyze.

        Returns
        -------
        tuple[bool, bool]
            A tuple of (contains_base_model, contains_str).
            Returns (False, False) if the type contains other types.
        """
        # Import here to avoid circular dependency
        from rdfantic.models.base import RdfanticBaseModel  # noqa: PLC0415

        if isinstance(item_type, types.UnionType):
            types_ = set(get_args(item_type))
            if not types_:
                return False, False
            contains_str = False
            contains_base_model = False
            for tp in types_:
                if issubclass(tp, str):
                    contains_str = True
                elif issubclass(tp, RdfanticBaseModel):
                    contains_base_model = True
                else:
                    return False, False
            return contains_base_model, contains_str
        elif isinstance(item_type, type):
            return issubclass(item_type, RdfanticBaseModel), issubclass(item_type, str)
        else:
            return False, False

    @classmethod
    def get_item_type(cls, annotation: Any) -> Any:
        """Recursively unwraps annotation to return the underlying item type.

        Args:
            annotation: The type annotation to unwrap.

        Returns
        -------
            The underlying item type after unwrapping Annotated, Sequence, and Union.
        """
        for extractor in (cls.get_annotated_type, cls.get_sequence_type, cls.get_union_type):
            if (item_type := extractor(annotation)) is not None:
                return cls.get_item_type(item_type)
        return annotation

    @classmethod
    def resolve_type_info(cls, annotation: Any) -> TypeInfo:
        """Return TypeInfo indicating if annotation is a list and its item type.

        Args:
            annotation: The type annotation to analyze.

        Returns
        -------
            TypeInfo indicating whether the annotation is a list and its item type.
        """
        if (item_type := cls.get_sequence_type(annotation)) is not None:
            return TypeInfo(is_list=True, item_type=item_type)
        if (item_type := cls.get_annotated_type(annotation)) is not None:
            return cls.resolve_type_info(item_type)
        if (item_type := cls.get_union_type(annotation)) is not None:
            # Check if the Union contains a Sequence type to determine if it's a list, otherwise treat as non-list
            sequence_type = cls.get_sequence_type(item_type)
            is_sequence = sequence_type is not None and sequence_type != item_type
            contains_none = type(None) in cls.get_union_types(annotation)
            return TypeInfo(
                is_list=is_sequence, item_type=cls.get_item_type(item_type), is_union=True, contains_none=contains_none
            )
        return TypeInfo(is_list=False, item_type=annotation)
