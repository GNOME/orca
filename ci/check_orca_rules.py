#!/usr/bin/python
"""Checks additional rules not covered by the other linters."""

# Each rule is a Rule subclass with a check() which takes a parsed file and yields the line and
# what is wrong with it. Rule also provides the tree walking a rule is likely to want. A line
# which has to break a rule can say so with a comment naming that rule:
#
#     the_awkward_line()  # orca-rules: the-name-of-the-rule

import ast
import pathlib
import sys
from collections.abc import Iterator
from typing import NamedTuple


class Problem(NamedTuple):
    """Something a rule check found."""

    line: int
    rule: str
    description: str

    def __str__(self) -> str:
        return f"{self.line}: {self.rule}: {self.description}"


class Rule:
    """Base class for rules Orca's code is expected to follow."""

    @staticmethod
    def check(tree: ast.Module) -> Iterator[tuple[int, str]]:
        """Yields the line and the description, for each break of this rule."""

        raise NotImplementedError

    @staticmethod
    def scopes(tree: ast.Module) -> Iterator[ast.AST]:
        """Yields the module and everything in it which has its own names."""

        yield tree
        for node in ast.walk(tree):
            if Rule.starts_a_scope(node):
                yield node

    @staticmethod
    def starts_a_scope(node: ast.AST) -> bool:
        """Returns True if the names in this node's body are its own."""

        return isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef))

    @staticmethod
    def nodes_in(scope: ast.AST) -> Iterator[ast.AST]:
        """Yields the nodes belonging to this scope, without descending into the ones inside it."""

        for child in ast.iter_child_nodes(scope):
            yield child
            if not Rule.starts_a_scope(child):
                yield from Rule.nodes_in(child)


class PrintMessageArguments(Rule):
    """Requires the message given to debug.print_message() to be a simple string."""

    # We want to limit print_message() to simple messages and use print_tokens() for everything
    # else. This prevents performance issues resulting from stringification which might be unused
    # due to the debug level. It will also make it possible to perform additional processing based
    # on the type of object, both during and post capture.

    @staticmethod
    def check(tree: ast.Module) -> Iterator[tuple[int, str]]:
        """Reports each print_message() whose message should make it a print_tokens() call."""

        for scope in Rule.scopes(tree):
            assigned = PrintMessageArguments._assignments_in(scope)
            for node in Rule.nodes_in(scope):
                if not PrintMessageArguments._is_a_print_message(node):
                    continue
                problem = PrintMessageArguments._problem_description(node, assigned)
                if problem:
                    yield node.lineno, problem

    @staticmethod
    def _is_a_print_message(node: ast.AST) -> bool:
        """Returns True if this is a call to debug.print_message() with a message."""

        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "print_message"
            and len(node.args) >= 2
        )

    @staticmethod
    def _assignments_in(scope: ast.AST) -> dict[str, list[tuple[int, ast.AST | None]]]:
        """Returns the line and the value of everything assigned to each name in this scope."""

        # A name assigned in a way we cannot read, such as a for loop target or unpacking, is
        # recorded with no value, which no message is allowed to rely on.
        assigned: dict[str, list[tuple[int, ast.AST | None]]] = {}
        for parameter in PrintMessageArguments._parameters_of(scope):
            PrintMessageArguments._record(assigned, parameter, 0, None)
        for node in Rule.nodes_in(scope):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    PrintMessageArguments._record_target(assigned, target, node.value, node.lineno)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                PrintMessageArguments._record_target(assigned, node.target, node.value, node.lineno)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                PrintMessageArguments._record_target(assigned, node.target, None, node.lineno)
            elif isinstance(node, ast.withitem):
                line = node.context_expr.lineno
                PrintMessageArguments._record_target(assigned, node.optional_vars, None, line)
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                # A comprehension binds its targets before the element, whatever the source order.
                for clause in node.generators:
                    PrintMessageArguments._record_target(assigned, clause.target, None, node.lineno)
            else:
                for name in PrintMessageArguments._names_bound_by(node):
                    PrintMessageArguments._record(assigned, name, node.lineno, None)
        return assigned

    @staticmethod
    def _record(
        assigned: dict[str, list[tuple[int, ast.AST | None]]],
        name: str,
        line: int,
        value: ast.AST | None,
    ) -> None:
        """Records that the name was given the value on this line."""

        assigned.setdefault(name, []).append((line, value))

    @staticmethod
    def _record_target(
        assigned: dict[str, list[tuple[int, ast.AST | None]]],
        target: ast.AST | None,
        value: ast.AST | None,
        line: int,
    ) -> None:
        """Records that everything assigned by target was given value on this line."""

        if target is None:
            return
        for node in ast.walk(target):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                # Unpacking gives a name one piece of something, which we cannot follow.
                whole = value if node is target else None
                PrintMessageArguments._record(assigned, node.id, line, whole)

    @staticmethod
    def _names_bound_by(node: ast.AST) -> list[str]:
        """Returns the names this node binds to something we cannot read."""

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            return [node.name]
        if isinstance(node, ast.alias):
            return [node.asname or node.name.split(".")[0]]
        if isinstance(node, ast.MatchMapping):
            return [node.rest] if node.rest else []
        if isinstance(node, (ast.MatchAs, ast.MatchStar, ast.ExceptHandler)):
            return [node.name] if node.name else []
        return []

    @staticmethod
    def _parameters_of(scope: ast.AST) -> list[str]:
        """Returns the names of this scope's parameters, which the caller decides."""

        if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return []
        arguments = scope.args
        taken = [*arguments.posonlyargs, *arguments.args, *arguments.kwonlyargs]
        if arguments.vararg:
            taken.append(arguments.vararg)
        if arguments.kwarg:
            taken.append(arguments.kwarg)
        return [argument.arg for argument in taken]

    @staticmethod
    def _problem_description(
        call: ast.Call, assigned: dict[str, list[tuple[int, ast.AST | None]]]
    ) -> str:
        """Returns what is wrong with the call's message, or an empty string if nothing is."""

        message = call.args[1]
        if PrintMessageArguments._is_a_literal_string(message, assigned, call.lineno):
            return ""
        if not isinstance(message, ast.Name):
            return "the message is not a literal string; use debug.print_tokens()"
        if not PrintMessageArguments._values_above(message, assigned, call.lineno):
            return (
                f"cannot tell what {message.id} holds here; "
                f"assign a literal string to it, or use debug.print_tokens()"
            )
        return (
            f"{message.id} is not always a literal string; give the message its own name, "
            f"or use debug.print_tokens()"
        )

    @staticmethod
    def _values_above(
        name: ast.Name, assigned: dict[str, list[tuple[int, ast.AST | None]]], line: int
    ) -> list[ast.AST | None]:
        """Returns everything assigned to the name above this line."""

        return [value for at, value in assigned.get(name.id, []) if at <= line]

    @staticmethod
    def _is_a_literal_string(
        node: ast.AST | None,
        assigned: dict[str, list[tuple[int, ast.AST | None]]],
        line: int,
        seen: frozenset[str] = frozenset(),
    ) -> bool:
        """Returns True if this is a string written out in the source."""

        literal = PrintMessageArguments._is_a_literal_string
        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        if isinstance(node, ast.JoinedStr):
            return not any(isinstance(part, ast.FormattedValue) for part in node.values)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return literal(node.left, assigned, line, seen) and literal(
                node.right, assigned, line, seen
            )
        if isinstance(node, ast.Name) and node.id not in seen:
            values = PrintMessageArguments._values_above(node, assigned, line)
            return bool(values) and all(
                literal(value, assigned, line, seen | {node.id}) for value in values
            )
        return False


class Checker:
    """Runs every rule over the files it is given."""

    @staticmethod
    def rules() -> dict[str, type[Rule]]:
        """Returns all the rules to be checked."""

        return {
            "print-message-arguments": PrintMessageArguments,
        }

    @staticmethod
    def check_file(path: str) -> list[Problem]:
        """Returns the list of Problems found in this file."""

        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        lines = source.splitlines()
        found = [
            Problem(line, name, description)
            for name, rule in Checker.rules().items()
            for line, description in rule.check(ast.parse(source))
            if f"orca-rules: {name}" not in lines[line - 1]
        ]
        return sorted(found)

    @staticmethod
    def check_files(paths: list[str]) -> int:
        """Prints the Problems found in each file. Returns the total number of violations."""

        problems = 0
        for path in paths:
            for problem in Checker.check_file(path):
                print(f"{path}:{problem}")  # noqa: T201
                problems += 1
        return problems


def main() -> int:
    """Checks each file named on the command line or src/orca/*.py."""

    paths = sys.argv[1:] or sorted(str(path) for path in pathlib.Path("src/orca").rglob("*.py"))
    return 1 if Checker.check_files(paths) else 0


if __name__ == "__main__":
    sys.exit(main())
