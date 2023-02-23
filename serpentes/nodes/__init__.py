from __future__ import annotations

from ast import (
    AST,
    AnnAssign,
    Assert,
    Assign,
    AsyncFor,
    AsyncFunctionDef,
    AsyncWith,
    Attribute,
    AugAssign,
    Await,
    BinOp,
    Break,
    Call,
    ClassDef,
    Compare,
    Constant,
    Continue,
    Delete,
    Dict,
    DictComp,
    ExceptHandler,
    Expr,
    For,
    FunctionDef,
    GeneratorExp,
    Global,
    If,
    IfExp,
    Import,
    ImportFrom,
    Lambda,
    List,
    ListComp,
)
from ast import Module as AModule
from ast import (
    Name,
    NamedExpr,
    Nonlocal,
    Pass,
    Raise,
    Return,
    Set,
    SetComp,
    Slice,
    Starred,
    Subscript,
    Try,
    Tuple,
    UnaryOp,
    While,
    With,
    Yield,
    YieldFrom,
    alias,
    arg,
    arguments,
    comprehension,
    keyword,
    withitem,
)
from functools import partial
from typing import Any, Generic, TypeVar

__all__ = (
    "Node",
    "Literals",
    "Variables",
    "Expressions",
    "Subscripting",
    "Comprehensions",
    "Controlflow",
    "Objects",
    "Module",
)

NodeT = TypeVar("NodeT")


class Node(Generic[NodeT]):
    ast: NodeT
    data: dict[str, Any]

    lineno: int
    end_lineno: int

    col_offset: int
    end_col_offset: int

    def __init__(self, **data: Any) -> None:
        meta = data.pop("meta")
        self.lineno = meta.line
        self.end_lineno = meta.end_line

        self.col_offset = meta.column
        self.end_col_offset = meta.end_column

        self.data = data
        self.ast = data.pop("ast")

    def __class_getitem__(cls: type[Node[Any]], ast: str | NodeT) -> partial[Node[NodeT]]:
        if isinstance(ast, str):
            return cls  # pyright: ignore

        return partial(cls, ast=ast)

    def build(self) -> NodeT:
        parsed: dict[str, AST] = {}

        def recurse(value: Node[Any] | list[Node[Any]]) -> Any:
            if isinstance(value, Node):
                return value.build()

            elif isinstance(value, list):  # pyright: ignore
                for index, node in enumerate(value):
                    value[index] = recurse(node)

                return value

            return value

        for name, value in self.data.items():
            parsed[name] = recurse(value)

        return self.ast(  # pyright: ignore
            **parsed,
            lineno=self.lineno,
            end_lineno=self.end_lineno,
            col_offset=self.col_offset,
            end_col_offset=self.end_col_offset,
        )


class Literals:
    Constant = Node[Constant]
    List = Node[List]
    Tuple = Node[Tuple]
    Set = Node[Set]
    Dict = Node[Dict]


class Variables:
    Name = Node[Name]
    Starred = Node[Starred]


class Expressions:
    Expr = Node[Expr]

    UnaryOp = Node[UnaryOp]
    BinOp = Node[BinOp]
    Compare = Node[Compare]

    Call = Node[Call]
    Keyword = Node[keyword]

    IfExp = Node[IfExp]

    Attribute = Node[Attribute]
    NamedExpr = Node[NamedExpr]


class Subscripting:
    Subscript = Node[Subscript]
    Slice = Node[Slice]


class Comprehensions:
    ListComp = Node[ListComp]
    SetComp = Node[SetComp]
    GeneratorExp = Node[GeneratorExp]
    DictComp = Node[DictComp]
    Comphrehension = Node[comprehension]


class Statements:
    Assign = Node[Assign]
    AnnAssign = Node[AnnAssign]
    AugAssign = Node[AugAssign]

    Raise = Node[Raise]
    Assert = Node[Assert]
    Delete = Node[Delete]
    Pass = Node[Pass]

    Import = Node[Import]
    ImprotFrom = Node[ImportFrom]

    Alias = Node[alias]


class Controlflow:
    If = Node[If]
    For = Node[For]
    While = Node[While]

    Break = Node[Break]
    Continue = Node[Continue]

    Try = Node[Try]
    ExceptHandler = Node[ExceptHandler]

    With = Node[With]
    WithItem = Node[withitem]


class Objects:
    Functiondef = Node[FunctionDef]
    Lambda = Node[Lambda]

    Arguments = Node[arguments]
    Arg = Node[arg]

    Return = Node[Return]
    Yield = Node[Yield]
    YieldFrom = Node[YieldFrom]

    Global = Node[Global]
    Nonlocal = Node[Nonlocal]

    ClassDef = Node[ClassDef]

    AsyncFunctionDef = Node[AsyncFunctionDef]
    Await = Node[Await]

    AsyncFor = Node[AsyncFor]
    AsyncWith = Node[AsyncWith]


Module = Node[AModule]
