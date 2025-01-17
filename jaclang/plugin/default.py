"""Jac Language Features."""

from __future__ import annotations

import os
import types
from dataclasses import field
from functools import wraps
from typing import Any, Callable, Optional, Type

from jaclang.compiler.absyntree import Module
from jaclang.compiler.constant import EdgeDir, colors
from jaclang.core.aott import aott_lower, aott_raise
from jaclang.core.construct import (
    Architype,
    DSFunc,
    EdgeAnchor,
    EdgeArchitype,
    GenericEdge,
    JacTestCheck,
    NodeAnchor,
    NodeArchitype,
    ObjectAnchor,
    Root,
    WalkerAnchor,
    WalkerArchitype,
    root,
)
from jaclang.core.importer import jac_importer
from jaclang.core.utils import traverse_graph
from jaclang.plugin.feature import JacFeature as Jac
from jaclang.plugin.spec import T


import pluggy


__all__ = [
    "EdgeAnchor",
    "GenericEdge",
    "JacTestCheck",
    "NodeAnchor",
    "ObjectAnchor",
    "WalkerAnchor",
    "NodeArchitype",
    "EdgeArchitype",
    "WalkerArchitype",
    "Architype",
    "DSFunc",
    "root",
    "Root",
    "jac_importer",
    "T",
]


hookimpl = pluggy.HookimplMarker("jac")


class JacFeatureDefaults:
    """Jac Feature."""

    pm = pluggy.PluginManager("jac")

    @staticmethod
    @hookimpl
    def make_architype(
        cls: type,
        arch_base: Type[Architype],
        on_entry: list[DSFunc],
        on_exit: list[DSFunc],
    ) -> Type[Architype]:
        """Create a new architype."""
        for i in on_entry + on_exit:
            i.resolve(cls)
        if not issubclass(cls, arch_base):
            cls = type(cls.__name__, (cls, arch_base), {})
        cls._jac_entry_funcs_ = on_entry  # type: ignore
        cls._jac_exit_funcs_ = on_exit  # type: ignore
        inner_init = cls.__init__  # type: ignore

        @wraps(inner_init)
        def new_init(self: Architype, *args: object, **kwargs: object) -> None:
            inner_init(self, *args, **kwargs)
            arch_base.__init__(self)

        cls.__init__ = new_init  # type: ignore
        return cls

    @staticmethod
    @hookimpl
    def make_obj(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a new architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=Architype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_node(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a obj architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=NodeArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_edge(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a edge architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=EdgeArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def make_walker(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]:
        """Create a walker architype."""

        def decorator(cls: Type[Architype]) -> Type[Architype]:
            """Decorate class."""
            cls = Jac.make_architype(
                cls=cls, arch_base=WalkerArchitype, on_entry=on_entry, on_exit=on_exit
            )
            return cls

        return decorator

    @staticmethod
    @hookimpl
    def jac_import(
        target: str,
        base_path: str,
        cachable: bool,
        override_name: Optional[str],
        mod_bundle: Optional[Module],
    ) -> Optional[types.ModuleType]:
        """Core Import Process."""
        result = jac_importer(
            target=target,
            base_path=base_path,
            cachable=cachable,
            override_name=override_name,
            mod_bundle=mod_bundle,
        )
        return result

    @staticmethod
    @hookimpl
    def create_test(test_fun: Callable) -> Callable:
        """Create a new test."""

        def test_deco() -> None:
            test_fun(JacTestCheck())

        test_deco.__name__ = test_fun.__name__
        JacTestCheck.add_test(test_deco)

        return test_deco

    @staticmethod
    @hookimpl
    def run_test(filename: str) -> bool:
        """Run the test suite in the specified .jac file.

        :param filename: The path to the .jac file.
        """
        if filename.endswith(".jac"):
            base, mod_name = os.path.split(filename)
            base = base if base else "./"
            mod_name = mod_name[:-4]
            JacTestCheck.reset()
            Jac.jac_import(target=mod_name, base_path=base)
            JacTestCheck.run_test()
        else:
            print("Not a .jac file.")
        return True

    @staticmethod
    @hookimpl
    def elvis(op1: Optional[T], op2: T) -> T:
        """Jac's elvis operator feature."""
        return ret if (ret := op1) is not None else op2

    @staticmethod
    @hookimpl
    def has_instance_default(gen_func: Callable[[], T]) -> T:
        """Jac's has container default feature."""
        return field(default_factory=lambda: gen_func())

    @staticmethod
    @hookimpl
    def spawn_call(op1: Architype, op2: Architype) -> WalkerArchitype:
        """Jac's spawn operator feature."""
        if isinstance(op1, WalkerArchitype):
            return op1._jac_.spawn_call(op2)
        elif isinstance(op2, WalkerArchitype):
            return op2._jac_.spawn_call(op1)
        else:
            raise TypeError("Invalid walker object")

    @staticmethod
    @hookimpl
    def report(expr: Any) -> Any:  # noqa: ANN401
        """Jac's report stmt feature."""

    @staticmethod
    @hookimpl
    def ignore(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's ignore stmt feature."""
        return walker._jac_.ignore_node(expr)

    @staticmethod
    @hookimpl
    def visit_node(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool:
        """Jac's visit stmt feature."""
        if isinstance(walker, WalkerArchitype):
            return walker._jac_.visit_node(expr)
        else:
            raise TypeError("Invalid walker object")

    @staticmethod
    @hookimpl
    def disengage(walker: WalkerArchitype) -> bool:  # noqa: ANN401
        """Jac's disengage stmt feature."""
        walker._jac_.disengage_now()
        return True

    @staticmethod
    @hookimpl
    def edge_ref(
        node_obj: NodeArchitype | list[NodeArchitype],
        target_obj: Optional[NodeArchitype | list[NodeArchitype]],
        dir: EdgeDir,
        filter_func: Optional[Callable[[list[EdgeArchitype]], list[EdgeArchitype]]],
        edges_only: bool,
    ) -> list[NodeArchitype] | list[EdgeArchitype]:
        """Jac's apply_dir stmt feature."""
        if isinstance(node_obj, NodeArchitype):
            node_obj = [node_obj]
        targ_obj_set: Optional[list[NodeArchitype]] = (
            [target_obj]
            if isinstance(target_obj, NodeArchitype)
            else target_obj if target_obj else None
        )
        if edges_only:
            connected_edges: list[EdgeArchitype] = []
            for node in node_obj:
                connected_edges += node._jac_.get_edges(
                    dir, filter_func, target_obj=targ_obj_set
                )
            return list(set(connected_edges))
        else:
            connected_nodes: list[NodeArchitype] = []
            for node in node_obj:
                connected_nodes.extend(
                    node._jac_.edges_to_nodes(dir, filter_func, target_obj=targ_obj_set)
                )
            return list(set(connected_nodes))

    @staticmethod
    @hookimpl
    def connect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        edge_spec: Callable[[], EdgeArchitype],
        edges_only: bool,
    ) -> list[NodeArchitype] | list[EdgeArchitype]:
        """Jac's connect operator feature.

        Note: connect needs to call assign compr with tuple in op
        """
        left = [left] if isinstance(left, NodeArchitype) else left
        right = [right] if isinstance(right, NodeArchitype) else right
        edges = []
        for i in left:
            for j in right:
                conn_edge = edge_spec()
                edges.append(conn_edge)
                i._jac_.connect_node(j, conn_edge)
        return right if not edges_only else edges

    @staticmethod
    @hookimpl
    def disconnect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        dir: EdgeDir,
        filter_func: Optional[Callable[[list[EdgeArchitype]], list[EdgeArchitype]]],
    ) -> bool:  # noqa: ANN401
        """Jac's disconnect operator feature."""
        disconnect_occurred = False
        left = [left] if isinstance(left, NodeArchitype) else left
        right = [right] if isinstance(right, NodeArchitype) else right
        for i in left:
            for j in right:
                edge_list: list[EdgeArchitype] = [*i._jac_.edges]
                edge_list = filter_func(edge_list) if filter_func else edge_list
                for e in edge_list:
                    if e._jac_.target and e._jac_.source:
                        if (
                            dir in ["OUT", "ANY"]  # TODO: Not ideal
                            and i._jac_.obj == e._jac_.source
                            and e._jac_.target == j._jac_.obj
                        ):
                            e._jac_.detach(i._jac_.obj, e._jac_.target)
                            disconnect_occurred = True
                        if (
                            dir in ["IN", "ANY"]
                            and i._jac_.obj == e._jac_.target
                            and e._jac_.source == j._jac_.obj
                        ):
                            e._jac_.detach(i._jac_.obj, e._jac_.source)
                            disconnect_occurred = True
        return disconnect_occurred

    @staticmethod
    @hookimpl
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]:
        """Jac's assign comprehension feature."""
        for obj in target:
            attrs, values = attr_val
            for attr, value in zip(attrs, values):
                setattr(obj, attr, value)
        return target

    @staticmethod
    @hookimpl
    def get_root() -> Architype:
        """Jac's assign comprehension feature."""
        return root

    @staticmethod
    @hookimpl
    def build_edge(
        is_undirected: bool,
        conn_type: Optional[Type[EdgeArchitype]],
        conn_assign: Optional[tuple[tuple, tuple]],
    ) -> Callable[[], EdgeArchitype]:
        """Jac's root getter."""
        conn_type = conn_type if conn_type else GenericEdge

        def builder() -> EdgeArchitype:
            edge = conn_type()
            edge._jac_.is_undirected = is_undirected
            if conn_assign:
                for fld, val in zip(conn_assign[0], conn_assign[1]):
                    if hasattr(edge, fld):
                        setattr(edge, fld, val)
                    else:
                        raise ValueError(f"Invalid attribute: {fld}")
            return edge

        return builder

    @staticmethod
    @hookimpl
    def with_llm(
        model: Any,  # noqa: ANN401
        model_params: dict[str, Any],
        incl_info: tuple,
        excl_info: tuple,
        inputs: tuple,
        outputs: tuple,
        action: str,
    ) -> Any:  # noqa: ANN401
        """Jac's with_llm feature."""
        reason = False
        if "reason" in model_params:
            reason = model_params.pop("reason")
        input_types_n_information_str = ""  # TODO: We have to generate this
        output_type_str = ""  # TODO: We have to generate this
        output_type_info_str = ""  # TODO: We have to generate this
        information_str = ""  # TODO: We have to generate this
        meaning_in = aott_raise(
            information_str,
            input_types_n_information_str,
            output_type_str,
            output_type_info_str,
            action,
            reason,
        )
        meaning_out = model.__infer__(meaning_in, **model_params)
        output_type_info = (None, None)  # TODO: We have to generate this
        return aott_lower(meaning_out, output_type_info)


class JacBuiltin:
    """Jac Builtins."""

    @staticmethod
    @hookimpl
    def dotgen(
        node: NodeArchitype,
        depth: int,
        traverse: bool,
        edge_type: list[str],
        bfs: bool,
        edge_limit: int,
        node_limit: int,
        dot_file: Optional[str],
    ) -> str:
        """Generate Dot file for visualizing nodes and edges."""
        edge_type = edge_type if edge_type else []
        visited_nodes: list[NodeArchitype] = []
        node_depths: dict[NodeArchitype, int] = {node: 0}
        queue: list = [[node, 0]]
        connections: list[tuple[NodeArchitype, NodeArchitype, EdgeArchitype]] = []

        def dfs(node: NodeArchitype, cur_depth: int) -> None:
            """Depth first search."""
            if node not in visited_nodes:
                visited_nodes.append(node)
                traverse_graph(
                    node,
                    cur_depth,
                    depth,
                    edge_type,
                    traverse,
                    connections,
                    node_depths,
                    visited_nodes,
                    queue,
                    bfs,
                    dfs,
                    node_limit,
                    edge_limit,
                )

        if bfs:
            cur_depth = 0
            while queue:
                current_node, cur_depth = queue.pop(0)
                if current_node not in visited_nodes:
                    visited_nodes.append(current_node)
                    traverse_graph(
                        current_node,
                        cur_depth,
                        depth,
                        edge_type,
                        traverse,
                        connections,
                        node_depths,
                        visited_nodes,
                        queue,
                        bfs,
                        dfs,
                        node_limit,
                        edge_limit,
                    )
        else:
            dfs(node, cur_depth=0)
        dot_content = (
            'digraph {\nnode [style="filled", shape="ellipse", '
            'fillcolor="invis", fontcolor="black"];\n'
        )
        for source, target, edge in connections:
            dot_content += (
                f"{visited_nodes.index(source)} -> {visited_nodes.index(target)} "
                f' [label="{edge._jac_.obj.__class__.__name__} "];\n'
            )
        for node_ in visited_nodes:
            color = (
                colors[node_depths[node_]] if node_depths[node_] < 25 else colors[24]
            )
            dot_content += f'{visited_nodes.index(node_)} [label="{node_._jac_.obj}" fillcolor="{color}"];\n'
        if dot_file:
            with open(dot_file, "w") as f:
                f.write(dot_content + "}")
        return dot_content + "}"


class JacCmdDefaults:
    """Jac CLI command."""

    @staticmethod
    @hookimpl
    def create_cmd() -> None:
        """Create Jac CLI cmds."""
        pass
