import multiprocessing as mp
from bidict import bidict
from typing import Union, List


class Node(object):
    def __init__(
        self,
        geoid: str,
        name: str = None,
        parent: str = None,
        level: str = None,
        abbr: str = None,
        nickname: Union[str, List[str]] = None,
    ):
        self.id = geoid
        self.level = level
        self.name = name
        self.parent = parent
        self.abbr = abbr
        self.nickname = nickname
        self.children = []

    def __repr__(self):
        rep = f"Node {self.geoid}"
        return rep

    def _json_repr(self):
        return bidict(
            {
                "id": self.id,
                "level": self.level,
                "name": self.name,
                "abbr": self.abbr,
                "nickname": self.nickname,
                "parent": self.parent,
                "children": self.children,
            }
        )

    def _generate_tree_dict(self):
        node_dict = self._json_repr()
        if self.children != []:  # If there are children
            with mp.Pool(
                mp.cpu_count() - 2
            ) as p:  # Leave 2 CPU cores free so you don't toast your CPU
                node_dict["children"] = {
                    child.id: child._generate_tree_dict() for child in self.children
                }
        return node_dict


class Tree(object):
    def __init__(self, root: Node):
        self.root = root
        self.jsonrepr = root._json_repr()

    def add_link(self, parent: Node, child: Node):
        child.parent = parent
        parent.children.append(child)

    def _generate_tree_dict(self, start_node: Node):
        node_dict = start_node._json_repr()
        cores = mp.cpu_count() - 2
        if start_node.children != []:  # If there are children
            with mp.Pool(cores) as p:
                child_nodes_json_list = p.map(
                    self._generate_tree_dict(), start_node.children
                )
                node_dict["children"] = {
                    child.id: child for child in child_nodes_json_list
                }
        return node_dict
