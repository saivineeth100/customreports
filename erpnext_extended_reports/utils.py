from typing import Union
from frappe import Any
from frappe.database.query import QueryBuilder
from frappe.query_builder import AliasedQuery
from pypika.utils import builder
from pypika.queries import Selectable
import types


def mysql_with_sql(self, **kwargs) -> str:
    is_recursive = False
    for clause in self._with:
        if isinstance(clause,WithQuery) and clause.is_recursive:
            is_recursive = True
            break

    return ("WITH recursive " if is_recursive else "WITH ") + ",".join(
        clause.name
        + " AS ("
        + clause.get_sql(subquery=False, with_alias=False, **kwargs)
        + ") "
        for clause in self._with
    )


class QueryBuilderWithPatcher:
    def __init__(self, instance):
        self.instance = instance
        self.active = False

    def patch(self):
        if not self.active:
            self.instance.patched_with_ = types.MethodType(
                builder(mysqlbuiderwith_), self.instance
            )
            self.active = True

    def unpatch(self):
        if self.active:
            delattr(self.instance, "patched_with_")
            self.active = False

    def __enter__(self):
        self.patch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()


class QueryBuilderWithSQLPatcher:
    def __init__(self, instance):
        self.instance = instance
        self.active = False

    def patch(self):
        if not self.active:
            self.original__with_sql_method = self.instance.original__with_sql_method
            self.instance._with_sql = types.MethodType(mysql_with_sql, self.instance)
            self.active = True

    def unpatch(self):
        if self.active:
            self.instance._with_sql = self.original__with_sql_method
            self.active = False

    def __enter__(self):
        self.patch()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unpatch()


# @classmethod
def with_(
    cls, table: Union[str, Selectable], name: str, **kwargs: Any
) -> "QueryBuilder":
    instance = cls._builder(**kwargs)
    with QueryBuilderWithPatcher(instance):
        return instance.patched_with_(table, name)


def mysqlbuiderwith_(self, selectable, name: str, is_recursive: bool = False):
    t = WithQuery(name, selectable, is_recursive)
    self._with.append(t)


class WithQuery(AliasedQuery):
    def __init__(self, name, query=None, is_recursive: bool = False):
        self.is_recursive = is_recursive
        super().__init__(name, query)
