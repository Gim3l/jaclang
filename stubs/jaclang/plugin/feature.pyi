import types
from _typeshed import Incomplete
from jaclang.compiler.constant import EdgeDir as EdgeDir
from jaclang.plugin.default import (
    Architype as Architype,
    EdgeArchitype as EdgeArchitype,
    JacFeatureDefaults as JacFeatureDefaults,
    NodeArchitype as NodeArchitype,
    Root as Root,
    T as T,
    WalkerArchitype as WalkerArchitype,
)
from jaclang.plugin.spec import DSFunc as DSFunc, JacFeatureSpec as JacFeatureSpec
from typing import Any, Callable, Optional, Type

class JacFeature:
    pm: Incomplete
    RootType: Type[Root]
    EdgeDir: Type[EdgeDir]
    @staticmethod
    def make_obj(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_node(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_edge(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def make_walker(
        on_entry: list[DSFunc], on_exit: list[DSFunc]
    ) -> Callable[[type], type]: ...
    @staticmethod
    def jac_import(
        target: str,
        base_path: str,
        cachable: bool = True,
        override_name: Optional[str] = None,
    ) -> Optional[types.ModuleType]: ...
    @staticmethod
    def create_test(test_fun: Callable) -> Callable: ...
    @staticmethod
    def run_test(filename: str) -> None: ...
    @staticmethod
    def elvis(op1: Optional[T], op2: T) -> T: ...
    @staticmethod
    def has_instance_default(gen_func: Callable) -> list[Any] | dict[Any, Any]: ...
    @staticmethod
    def spawn_call(op1: Architype, op2: Architype) -> Architype: ...
    @staticmethod
    def report(expr: Any) -> Any: ...
    @staticmethod
    def ignore(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool: ...
    @staticmethod
    def visit_node(
        walker: WalkerArchitype,
        expr: list[NodeArchitype | EdgeArchitype] | NodeArchitype | EdgeArchitype,
    ) -> bool: ...
    @staticmethod
    def disengage(walker: WalkerArchitype) -> bool: ...
    @staticmethod
    def edge_ref(
        node_obj: NodeArchitype,
        dir: EdgeDir,
        filter_type: Optional[type],
        filter_func: Optional[Callable],
    ) -> list[NodeArchitype]: ...
    @staticmethod
    def connect(
        left: NodeArchitype | list[NodeArchitype],
        right: NodeArchitype | list[NodeArchitype],
        edge_spec: EdgeArchitype,
    ) -> NodeArchitype | list[NodeArchitype]: ...
    @staticmethod
    def disconnect(op1: Optional[T], op2: T, op: Any) -> T: ...
    @staticmethod
    def assign_compr(
        target: list[T], attr_val: tuple[tuple[str], tuple[Any]]
    ) -> list[T]: ...
    @staticmethod
    def get_root() -> Architype: ...
    @staticmethod
    def build_edge(
        edge_dir: EdgeDir,
        conn_type: Optional[Type[Architype]],
        conn_assign: Optional[tuple[tuple, tuple]],
    ) -> Architype: ...