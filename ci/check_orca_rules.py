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

Assignments = dict[str, list[tuple[int, ast.AST | None]]]


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

    @staticmethod
    def assignments_in(scope: ast.AST) -> Assignments:  # pylint: disable=too-many-branches
        """Returns the line and the value of everything assigned to each name in this scope."""

        # A name assigned in a way we cannot read, such as a for loop target or unpacking, is
        # recorded with no value, so no rule treats it as known.
        assigned: Assignments = {}
        for parameter in Rule._parameters_of(scope):
            Rule._record(assigned, parameter, 0, None)
        for node in Rule.nodes_in(scope):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    Rule._record_target(assigned, target, node.value, node.lineno)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                Rule._record_target(assigned, node.target, node.value, node.lineno)
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                Rule._record_target(assigned, node.target, None, node.lineno)
            elif isinstance(node, ast.Delete):
                for target in node.targets:
                    Rule._record_target(assigned, target, None, node.lineno)
            elif sys.version_info >= (3, 12) and isinstance(node, ast.TypeAlias):
                Rule._record_target(assigned, node.name, None, node.lineno)
            elif isinstance(node, (ast.Global, ast.Nonlocal)):
                # The name belongs to another scope for the whole of this one, so we cannot read it.
                for name in node.names:
                    Rule._record(assigned, name, 0, None)
            elif isinstance(node, ast.withitem):
                Rule._record_target(assigned, node.optional_vars, None, node.context_expr.lineno)
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                # A comprehension binds its targets before the expression which uses them.
                for clause in node.generators:
                    Rule._record_target(assigned, clause.target, None, node.lineno)
            else:
                for name in Rule._names_bound_by(node):
                    Rule._record(assigned, name, node.lineno, None)
        return assigned

    @staticmethod
    def _record(assigned: Assignments, name: str, line: int, value: ast.AST | None) -> None:
        """Records that the name was given the value on this line."""

        assigned.setdefault(name, []).append((line, value))

    @staticmethod
    def _record_target(
        assigned: Assignments, target: ast.AST | None, value: ast.AST | None, line: int
    ) -> None:
        """Records that everything assigned by target was given value on this line."""

        if target is None:
            return
        for node in ast.walk(target):
            if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
                # Unpacking gives each name part of the value, and we cannot tell which part.
                whole = value if node is target else None
                Rule._record(assigned, node.id, line, whole)

    @staticmethod
    def _names_bound_by(node: ast.AST) -> list[str]:
        """Returns the names this node binds, whose values we cannot read."""

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
        """Returns the names of this scope's parameters."""

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
    def values_above(name: ast.Name, assigned: Assignments, line: int) -> list[ast.AST | None]:
        """Returns everything assigned to the name above this line."""

        return [value for at, value in assigned.get(name.id, []) if at <= line]

    @staticmethod
    def is_literal_string(
        node: ast.AST | None,
        assigned: Assignments,
        line: int,
        seen: frozenset[str] = frozenset(),
    ) -> bool:
        """Returns True if this is a string written out in the source."""

        literal = Rule.is_literal_string
        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        if isinstance(node, ast.JoinedStr):
            return not any(isinstance(part, ast.FormattedValue) for part in node.values)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return literal(node.left, assigned, line, seen) and literal(
                node.right, assigned, line, seen
            )
        if isinstance(node, ast.Name) and node.id not in seen:
            values = Rule.values_above(node, assigned, line)
            return bool(values) and all(
                literal(value, assigned, line, seen | {node.id}) for value in values
            )
        return False

    @staticmethod
    def calls(node: ast.AST, name: str, arguments: int) -> bool:
        """Returns True if this is a call to name() with at least that many arguments."""

        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == name
            and len(node.args) >= arguments
        )


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
            assigned = Rule.assignments_in(scope)
            for node in Rule.nodes_in(scope):
                if not isinstance(node, ast.Call) or not Rule.calls(node, "print_message", 2):
                    continue
                problem = PrintMessageArguments._problem_description(node, assigned)
                if problem:
                    yield node.lineno, problem

    @staticmethod
    def _problem_description(call: ast.Call, assigned: Assignments) -> str:
        """Returns what is wrong with the call's message, or an empty string if nothing is."""

        message = call.args[1]
        if Rule.is_literal_string(message, assigned, call.lineno):
            return ""
        if not isinstance(message, ast.Name):
            return "the message is not a literal string; use debug.print_tokens()"
        if not Rule.values_above(message, assigned, call.lineno):
            return (
                f"cannot tell what {message.id} holds here; "
                f"assign a literal string to it, or use debug.print_tokens()"
            )
        return (
            f"{message.id} is not always a literal string; give the message its own name, "
            f"or use debug.print_tokens()"
        )


class PrintTokensItems(Rule):
    """Requires each item of a debug.print_tokens() token list to be text or a value, not both."""

    # Only the items visible at the call are checked. A list built in another function is not.

    @staticmethod
    def check(tree: ast.Module) -> Iterator[tuple[int, str]]:
        """Reports each token item which mixes text with a value."""

        for scope in Rule.scopes(tree):
            assigned = Rule.assignments_in(scope)
            added = PrintTokensItems._items_added_in(scope)
            for node in Rule.nodes_in(scope):
                if isinstance(node, ast.Call) and Rule.calls(node, "print_tokens", 2):
                    yield from PrintTokensItems._problems_at(node, assigned, added)

    @staticmethod
    def _items_added_in(scope: ast.AST) -> dict[str, list[tuple[int, ast.AST]]]:
        """Returns the line and the item for each item added to a list in this scope."""

        added: dict[str, list[tuple[int, ast.AST]]] = {}
        for node in Rule.nodes_in(scope):
            for name, item in PrintTokensItems._items_added_by(node):
                added.setdefault(name, []).append((node.lineno, item))
        return added

    @staticmethod
    def _items_added_by(node: ast.AST) -> list[tuple[str, ast.AST]]:
        """Returns the list's name and the item, for each item this node adds to a list."""

        if isinstance(node, ast.Call):
            return PrintTokensItems._items_added_by_call(node)
        if isinstance(node, ast.AugAssign) and isinstance(node.op, ast.Add):
            if isinstance(node.target, ast.Name):
                name = node.target.id
                return [(name, item) for item in PrintTokensItems._items_of(node.value)]
            return []
        if isinstance(node, ast.AnnAssign):
            if node.value is None:
                return []
            targets: list[ast.AST] = [node.target]
            value: ast.AST = node.value
        elif isinstance(node, ast.Assign):
            targets = list(node.targets)
            value = node.value
        else:
            return []
        found = []
        for target in targets:
            if not isinstance(target, ast.Subscript) or not isinstance(target.value, ast.Name):
                continue
            if isinstance(target.slice, ast.Slice):
                name = target.value.id
                found += [(name, item) for item in PrintTokensItems._items_of(value)]
            else:
                found.append((target.value.id, value))
        return found

    @staticmethod
    def _items_added_by_call(call: ast.Call) -> list[tuple[str, ast.AST]]:
        """Returns the list's name and the item, for each item this call adds to a list."""

        if not isinstance(call.func, ast.Attribute) or not isinstance(call.func.value, ast.Name):
            return []
        name, arguments = call.func.value.id, call.args
        if call.func.attr == "append" and len(arguments) == 1:
            return [(name, arguments[0])]
        if call.func.attr == "insert" and len(arguments) == 2:
            return [(name, arguments[1])]
        if call.func.attr == "extend" and len(arguments) == 1:
            return [(name, item) for item in PrintTokensItems._items_of(arguments[0])]
        return []

    @staticmethod
    def _items_of(values: ast.AST) -> list[ast.AST]:
        """Returns the items of a list written in place, or nothing if it is not one."""

        if isinstance(values, (ast.List, ast.Tuple)):
            return list(values.elts)
        return []

    @staticmethod
    def _problems_at(
        call: ast.Call, assigned: Assignments, added: dict[str, list[tuple[int, ast.AST]]]
    ) -> Iterator[tuple[int, str]]:
        """Reports the items of this call's token list which mix text with a value."""

        tokens = call.args[1]
        if isinstance(tokens, (ast.List, ast.Tuple)):
            for item in tokens.elts:
                yield from PrintTokensItems._problem_with(item)
            return
        if not isinstance(tokens, ast.Name):
            return
        for value in Rule.values_above(tokens, assigned, call.lineno):
            for item in PrintTokensItems._items_of(value):
                yield from PrintTokensItems._problem_with(item)
        for at, item in added.get(tokens.id, []):
            if at <= call.lineno:
                yield from PrintTokensItems._problem_with(item)

    @staticmethod
    def _problem_with(item: ast.AST) -> Iterator[tuple[int, str]]:
        """Reports this item, or the items unpacked into it, if it mixes text with a value."""

        if isinstance(item, ast.Starred):
            for spread in PrintTokensItems._items_of(item.value):
                yield from PrintTokensItems._problem_with(spread)
            return
        if PrintTokensItems._mixes_text_and_value(item):
            yield (
                item.lineno,
                "this token mixes text with a value; give the text and the value their own items",
            )

    @staticmethod
    def _mixes_text_and_value(item: ast.AST) -> bool:
        """Returns True if this item is text with a value built into it."""

        text = PrintTokensItems._is_text
        if isinstance(item, ast.JoinedStr):
            return any(isinstance(part, ast.FormattedValue) for part in item.values)
        if isinstance(item, ast.Call):
            if isinstance(item.func, ast.Attribute):
                return item.func.attr == "format"
            return isinstance(item.func, ast.Name) and item.func.id in ("str", "repr", "format")
        if isinstance(item, ast.BinOp) and isinstance(item.op, ast.Mod):
            return text(item.left)
        if isinstance(item, ast.BinOp) and isinstance(item.op, ast.Add):
            mixes = PrintTokensItems._mixes_text_and_value
            return mixes(item.left) or mixes(item.right) or text(item.left) != text(item.right)
        return False

    @staticmethod
    def _is_text(node: ast.AST) -> bool:
        """Returns True if this is a string written in place, rather than a value."""

        if isinstance(node, ast.Constant):
            return isinstance(node.value, str)
        if isinstance(node, ast.JoinedStr):
            return not any(isinstance(part, ast.FormattedValue) for part in node.values)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            return PrintTokensItems._is_text(node.left) and PrintTokensItems._is_text(node.right)
        return False


class Checker:
    """Runs every rule over the files it is given."""

    @staticmethod
    def rules() -> dict[str, type[Rule]]:
        """Returns all the rules to be checked."""

        return {
            "print-message-arguments": PrintMessageArguments,
            "print-tokens-items": PrintTokensItems,
        }

    @staticmethod
    def check_file(path: str) -> list[Problem]:
        """Returns the list of Problems found in this file."""

        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        lines = source.splitlines()
        found = {
            Problem(line, name, description)
            for name, rule in Checker.rules().items()
            for line, description in rule.check(ast.parse(source))
            if not Checker._is_allowed(lines, line, name)
        }
        return sorted(found)

    @staticmethod
    def _is_allowed(lines: list[str], line: int, rule: str) -> bool:
        """Returns True if this line, or the one above it, has a comment naming this rule."""

        allowed = f"orca-rules: {rule}"
        return allowed in lines[line - 1] or (line > 1 and allowed in lines[line - 2])

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
