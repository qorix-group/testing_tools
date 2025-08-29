#!/usr/bin/env python3

import argparse
import sys
from enum import Flag, StrEnum, auto
from typing import IO, Iterator, Optional  # noqa: UP035 Iterator from typing is expected here


class ItemType(StrEnum):
    """
    Enum representing different item types in crate structure.
    """

    CRATE = "crate"
    MOD = "mod"
    STRUCT = "struct"
    ENUM = "enum"
    TYPE = "type"
    TRAIT = "trait"
    FN = "fn"
    CONST_FN = "const fn"
    ASYNC_FN = "async fn"
    UNSAFE_FN = "unsafe fn"


class ItemTypeFlag(Flag):
    """
    Enum representing flags for item types.
    Allows combining multiple item types using bitwise operations.
    """

    CRATE = auto()
    MOD = auto()
    STRUCT = auto()
    ENUM = auto()
    TYPE = auto()
    TRAIT = auto()
    FN = auto()
    CONST_FN = auto()
    ASYNC_FN = auto()
    UNSAFE_FN = auto()

    ALL_FN = FN | CONST_FN | ASYNC_FN | UNSAFE_FN


class Visibility(StrEnum):
    """
    Enum representing visibility levels in crate.
    """

    PUB = "pub"
    PUB_CRATE = "pub(crate)"
    PUB_SELF = "pub(self)"
    PUB_SUPER = "pub(super)"


class InputLine:
    """
    Represents a line of raw input splitted to data and optional comment.
    """

    def __init__(self, line: str):
        """
        Initialize InputLine with data and optional comment.

        Parameters
        ----------
        line : str
            The input line to process.
        """
        line_parts = line.split("\t")

        self.data = line_parts[0]
        self.comment = line_parts[-1] if len(line_parts) > 1 else None
        self.tab_count = line.count("\t") if self.comment else None

    def has_comment(self) -> bool:
        """
        Check if the line has a comment.
        """
        return self.comment is not None

    def get_full_line(self) -> str:
        """
        Get the full line including data and comment.
        """
        return self.data + (("\t" * self.tab_count + self.comment) if self.has_comment() else "")

    def __str__(self) -> str:
        return f"InputLine(data='{self.data}', comment='{self.comment}', tab_count={self.tab_count})"


class Entry:
    """
    Represents an entry in the crate structure with metadata.
    """

    def __init__(self, line: str, item_type: ItemType, find_index: int):
        """
        Initialize Entry with line, item type, and index where the item type is found.
        Computes nest level and parses visibility and name from the line.

        Parameters
        ----------
        line : str
            The input line representing the entry.
        item_type : ItemType
            The type of the item represented by this entry.
        find_index : int
            The index where the item type is found in the line.
        """
        self.line = InputLine(line)
        self.item_type = item_type
        self.name = self._find_name(self.line.data)
        self.nest_level = self._compute_nest_level(find_index)
        self.visibility = self._find_visibility(self.line.data)

    def _compute_nest_level(self, find_index: int) -> int:
        """
        Compute the nesting level based on the index where the item type is found.

        Parameters
        ----------
        find_index : int
            The index where the item type is found in the line.
        """
        indent_size = 4
        return (find_index + 2) // indent_size  # +2 as we match with "─ " at the start

    def _find_visibility(self, data_line: str) -> Visibility:
        """
        Find the visibility of the item in the data line.

        Parameters
        ----------
        data_line : str
            The line of data to check for visibility.
        """
        tokens = data_line.split()

        if tokens[0] == "crate":
            # Crate has no visibility specifier, set pub for convenience
            return Visibility.PUB

        tokens.reverse()
        for token in tokens:
            token = token.strip()
            if token.startswith("pub"):
                return Visibility(token)

        raise RuntimeError(f"Visibility not detected for: {data_line}")

    def _find_name(self, data_line: str) -> str:
        """
        Find the name of the item in the data line.
        """
        tokens = data_line.split()

        if tokens[0] == "crate":  # Crate name does not end with colon
            return f"{tokens[0]}_{tokens[1]}"  # crate <module_name>

        tokens.reverse()
        for ndx, token in enumerate(tokens):
            token = token.strip()
            if token.endswith(":"):
                return f"{tokens[ndx + 1]}_{token[:-1]}"

        raise RuntimeError("Name not detected for: {data_line}")

    def __str__(self) -> str:
        return (
            f"Entry(line={self.line}, name={self.name}, item_type={self.item_type}, "
            f"nest_level={self.nest_level}, visibility={self.visibility})"
        )


class Indexer:
    """
    Simple indexer to iterate through a range of indices.
    """

    def __init__(self, ndx_count: int):
        """
        Initialize Indexer with the count of indices.

        Parameters
        ----------
        ndx_count : int
            The total number of indices to iterate through.
        """
        self.value = None
        self.ndx_count = ndx_count

    def _raise_if_invalid_range(self, new_val: int) -> None:
        """
        Raise IndexError if the new value is out of range.

        Parameters
        ----------
        new_val : int
            The new index value to check.
        """
        if new_val >= self.ndx_count:
            raise IndexError("Indexer out of range")

    def next(self) -> int:
        """
        Get the next index and increment the indexer.
        Raises IndexError if the indexer is out of range.
        """
        if self.value is None:
            self.value = 0
        else:
            new_value = self.value + 1
            self._raise_if_invalid_range(new_value)
            self.value = new_value

        return self.value

    def next_no_inc(self) -> int:
        """
        Get the next index without incrementing the indexer.
        Raises IndexError if the indexer is not started.
        """
        if self.value is None:
            raise RuntimeError("Indexer not started")

        new_value = self.value + 1
        self._raise_if_invalid_range(new_value)
        return new_value


class TreeNode:
    """
    Represents a node in the tree structure of crate items.
    Each node can have children and contains metadata about the item.
    """

    def __init__(self, entries: list[Entry], ndx: Indexer, parent: Optional["TreeNode"] = None):
        """
        Initialize TreeNode with entries, indexer, and optional parent node.

        Parameters
        ----------
        entries : list[Entry]
            List of Entry objects representing the crate structure.
        ndx : Indexer
            Indexer to track the current position in the entries.
        parent : TreeNode | None
            Parent node in the tree structure, if any.
        """
        self.metadata = set()
        try:
            entry = entries[ndx.next()]

            self.line = entry.line
            self.name = entry.name
            self.unique_name = f"{parent.unique_name}::{self.name}" if parent is not None else self.name
            self.item_type = entry.item_type
            self.visibility = entry.visibility
            self.parent = parent
            self.children = []

            nest_level = entry.nest_level

            while True:
                next_entry = entries[ndx.next_no_inc()]

                if next_entry.nest_level > nest_level:
                    self.children.append(TreeNode(entries, ndx, self))
                else:
                    return

        except IndexError:
            return

    def traverse_depth_first_pre_order(self) -> Iterator["TreeNode"]:
        """
        Traverse the tree in depth-first pre-order.
        """
        yield self

        for child in self.children:
            yield from child.traverse_depth_first_pre_order()

    def traverse_depth_first_post_order(self) -> Iterator["TreeNode"]:
        """
        Traverse the tree in depth-first post-order.
        """
        for child in self.children:
            yield from child.traverse_depth_first_post_order()

        yield self


class Tree:
    """
    A tree structure representing the crate items.
    Provides methods to filter nodes by visibility and item type.
    """

    def __init__(self, entries: list[Entry]):
        """
        Initialize Tree with a list of Entry objects.

        Parameters
        ----------
        entries : list[Entry]
            List of Entry objects representing the crate structure.
        """
        self.root = TreeNode(entries, Indexer(len(entries)))

    def write(self, target: IO[str]) -> None:
        """
        Write the tree structure to the target output stream.

        Parameters
        ----------
        target : IO[str]
            The output stream to write the tree structure to.
        """
        for node in self.root.traverse_depth_first_pre_order():
            target.write(f"{node.line.get_full_line()}\n")

    def filter_visibility(self, visibility: Visibility) -> None:
        """
        Filter the tree nodes by visibility.

        Parameters
        ----------
        visibility : Visibility
            The visibility level to filter nodes by.
        """
        for node in self.root.traverse_depth_first_pre_order():
            children_to_remove = []
            for ndx, child in enumerate(node.children):
                if child.visibility != visibility:
                    children_to_remove.append(ndx)

            for ndx in reversed(children_to_remove):
                del node.children[ndx]

    def filter_item_type(self, item_type_flag: ItemTypeFlag) -> None:
        """
        Filter the tree nodes by item type.

        Parameters
        ----------
        item_type_flag : ItemTypeFlag
            The item type flag to filter nodes by.
        """
        for node in self.root.traverse_depth_first_post_order():
            children_to_remove = []
            # Check if any child has the matching item type
            for ndx, child in enumerate(node.children):
                any_flag_present = False

                # ItemTypeFlag can consist of multiple ItemType
                for flag in item_type_flag:
                    item_type = ItemType[flag.name]
                    if child.item_type == item_type:
                        any_flag_present = True
                        break

                if any_flag_present or ("has_matching_type" in child.metadata):
                    node.metadata.add("has_matching_type")
                else:
                    children_to_remove.append(ndx)

            # Remove children that do not match the item type
            for ndx in reversed(children_to_remove):
                del node.children[ndx]

    def _find_node_by_unique_name(self, unique_name: str) -> TreeNode:
        """
        Find a node in the tree by its unique name.

        Parameters
        ----------
        unique_name : str
            The unique name of the node to find.
        """
        for node in self.root.traverse_depth_first_pre_order():
            if node.unique_name == unique_name:
                return node

        raise RuntimeError(f"Node with unique name '{unique_name}' not found")

    def add_comments_from_reference(self, reference_tree: "Tree") -> None:
        """
        Add comments from the reference tree to the current tree.
        Comments are added to nodes with matching unique names.
        """
        for ref_node in reference_tree.root.traverse_depth_first_pre_order():
            try:
                node = self._find_node_by_unique_name(ref_node.unique_name)
                if ref_node.line.has_comment():
                    node.line.comment = ref_node.line.comment
                    node.line.tab_count = ref_node.line.tab_count
            except RuntimeError:
                sys.stderr.write(
                    f"Warning: Reference node with unique name '{ref_node.unique_name}' not found "
                    "in the current tree.\n",
                )

    def count_leaf_nodes(self) -> int:
        """
        Count the number of leaf nodes in the tree.
        A leaf node is defined as a node with no children.
        """
        count = 0
        for node in self.root.traverse_depth_first_pre_order():
            if not node.children:
                count += 1
        return count

    def count_leaf_nodes_with_comment(self, comment: str) -> int:
        """
        Count the number of leaf nodes that have a comment starting with the specified string.

        Parameters
        ----------
        comment : str
            The comment string to match against leaf nodes' comments.
        """
        count = 0
        for node in self.root.traverse_depth_first_pre_order():
            if not node.children and node.line.has_comment() and node.line.comment.startswith(comment):
                count += 1
        return count


def process_line(line: str) -> Entry:
    """
    Process a single line of input and return an Entry object.

    Parameters
    ----------
    line : str
        The input line to process.
    """
    if line.startswith("crate"):
        return Entry(line, ItemType.CRATE, 0)

    for item_type in ItemType:
        found = line.find(f"─ {item_type.value} ")
        if found != -1:
            return Entry(line, item_type, found)

    raise RuntimeError(f"No known item type found for parsed line: {line}")


def process_input(input_lines: list[str]) -> list[Entry]:
    """
    Process a list of input lines and return a list of Entry objects.

    Parameters
    ----------
    input_lines : list[str]
        List of input lines to process.
    """
    data = []

    for line in input_lines:
        # We cannot remove leading spaces, as they are part of the structure
        line = line.rstrip()
        if len(line) == 0:
            continue

        entry = process_line(line)
        data.append(entry)

    return data


def process_args() -> argparse.Namespace:
    """
    Process command line arguments.
    """
    parser = argparse.ArgumentParser(description="Filter and compare Rust crate structure")
    parser.add_argument(
        "-v",
        "--visibility",
        type=str,
        choices=[v.name for v in Visibility],
        default=Visibility.PUB.name,
        help=f"Visibility to filter (default: {Visibility.PUB.name})",
    )
    parser.add_argument(
        "-t",
        "--item-type",
        type=str,
        choices=[v.name for v in ItemTypeFlag] + [ItemTypeFlag.ALL_FN.name],
        default=ItemTypeFlag.ALL_FN.name,
        help=f"Item type to focus on (default: {ItemTypeFlag.ALL_FN.name})",
    )
    parser.add_argument(
        "input",
        type=str,
        help="'cargo modules structure --package <package>' output file",
    )
    parser.add_argument(
        "-r",
        "--reference",
        type=str,
        default=None,
        help="Reference result created by this script to copy comments from",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="File to write output to (default: stdout)",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = process_args()

    with open(args.input) as f:
        input_lines = f.readlines()

    tree = Tree(process_input(input_lines))
    tree.filter_visibility(Visibility[args.visibility])
    tree.filter_item_type(ItemTypeFlag[args.item_type])

    if args.reference:
        with open(args.reference) as f:
            reference_lines = f.readlines()

        ref_tree = Tree(process_input(reference_lines))
        tree.add_comments_from_reference(ref_tree)

    if args.output:
        with open(args.output, "w") as f:
            tree.write(f)
    else:
        tree.write(sys.stdout)

    all_nodes = tree.count_leaf_nodes()
    if all_nodes == 0:
        raise RuntimeError("No leaf nodes found in the tree.")

    covered_nodes = tree.count_leaf_nodes_with_comment("YES")
    print(f"Coverage rate: {covered_nodes}/{all_nodes} ({covered_nodes / all_nodes * 100:.2f}%)", file=sys.stderr)  # noqa: T201 Printing status to stderr
