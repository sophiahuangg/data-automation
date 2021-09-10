# This idea is discontinued for the time being
# We are using simple lookups for location encoding now

import json
import multiprocessing as mp
import pandas as pd
import us

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
        rep = f"Node {self.id}"
        return rep

    def _json_repr(self):
        return {
            "id": self.id,
            "level": self.level,
            "name": self.name,
            "abbr": self.abbr,
            "nickname": self.nickname,
            # "parent": self.parent,
            # "children": self.children,
        }


class Tree(object):
    def __init__(self, root: Node):
        self.root = root
        self.jsonrepr = root._json_repr()

    def add_link(self, parent: Node, child: Node):
        child.parent = parent.id
        parent.children.append(child)

    def _generate_tree_dict(self, start_node: Node, parallel: bool = False):
        node_dict = start_node._json_repr()
        cores = mp.cpu_count() - 2
        if start_node.children != [] and parallel:  # If there are children
            with mp.Pool(cores) as p:
                child_nodes_json_list = p.map(
                    self._generate_tree_dict, start_node.children
                )
                node_dict["children"] = {
                    child["id"]: child for child in child_nodes_json_list
                }
        elif start_node.children != [] and not parallel:
            node_dict["children"] = {
                child.id: child._json_repr for child in start_node.children
            }
        return node_dict

    def save_tree(self, start_node: Node, fname: str):
        dict_to_save = self._generate_tree_dict(start_node=start_node)
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(dict_to_save, f, ensure_ascii=False, indent=4)
        return dict_to_save

    def traverse_keys(self, *args):
        """Traverses the tree down a set of keys and returns the output"""
        treedict = self._generate_tree_dict
        sub = treedict
        for arg in args:
            try:
                sub = sub[arg]
            except KeyError:
                print(
                    f"Error: Please choose valid keys (node IDs). Key {arg} does not exist."
                )
        return sub


if __name__ == "__main__":
    root = Node(geoid="69420", name="United States", level="country", abbr="US")

    extree = Tree(root=root)

    # ------------------------
    # Add state data to the tree
    # ------------------------

    states = us.states.STATES
    nodes = [
        Node(geoid=str(state.fips), name=str(state.name), abbr=str(state.abbr))
        for state in states
    ]
    for node in nodes:
        extree.add_link(parent=extree.root, child=node)

    # ------------------------
    # Merge in CBSA data
    # ------------------------

    cbsas = pd.read_csv("datasets/cbsas.csv")

    # Filter out the repeat CBSAs
    no_counties = cbsas.drop_duplicates(subset=["CBSA Code"])

    # Get rid of CBSAs that don't have names
    no_counties.dropna(inplace=True, subset=["CBSA Title"])
    no_counties["FIPS State Code"] = (
        no_counties["FIPS State Code"]
        .astype(int)
        .astype(str)
        .str.pad(width=2, fillchar="0")
    )

    for index, row in no_counties.iterrows():
        id = row["CBSA Code"]
        name = row["CBSA Title"].split(",")[0]
        state = row["FIPS State Code"]
        node = Node(geoid=id, name=name)

        print(id)
        print(name)
        print(state)

        # Find the state the node belongs to
        for statenode in extree.root.children:
            if str(statenode.id) == str(state):
                extree.add_link(parent=statenode, child=node)
                break

    extree.save_tree(start_node=root, fname="statetree.json")
