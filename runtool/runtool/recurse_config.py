# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

import itertools
from functools import singledispatch
from itertools import chain, product
from typing import Any, Callable

from runtool.datatypes import (
    Algorithm,
    Algorithms,
    Dataset,
    Datasets,
    Experiments,
)


class Versions:
    """
    The `Versions` class is used to represent an object which can
    take several different values. These different values are passed
    as a list when initializing the Versions object.

    >>> Versions([1, 2, 3])
    Versions([1, 2, 3])
    """

    def __init__(self, versions: list = None):
        self.__root__ = versions if versions else []

    def __repr__(self):
        if len(self) == 1:
            return repr(self[0])
        return f"Versions({self.__root__})"

    def __getitem__(self, item):
        return self.__root__[item]

    def __len__(self):
        return len(self.__root__)

    def __iter__(self):
        return iter(self.__root__)

    def __eq__(self, other):
        if isinstance(other, Versions):
            return self.__root__ == other.__root__
        return False

    def append(self, data: Any):
        self.__root__.append(data)

    def __mul__(
        self,
        other: "Versions",
    ) -> Experiments:
        """
        Calculates the cartesian product of all items in self and other and
        therafter calls __mul__ on each combination. Any `Experiments` objects
        generated is merged into one `Experiments` object.

        NOTE:
            This multiplication requires that the items in `self`
            and `other` produce `Experiments` objects when `__mul__`
            is called. Some classes which fullfill this criteria:

            * `Algorithm`
            * `Dataset`
            * `Algorithms`
            * `Datasets`

        In the below example we multiply two `Versions` objects.
        One of them contains two `Algorithm` objects and the other
        contains two `Dataset` objects. Multiplying these two objects
        generate a `Experiments` object of lenght 4 containing all
        combinations of the two `Versions` objects.

        >>> algorithm_1 = Algorithm({"image": "1", "instance": "1"})
        >>> algorithm_2 = Algorithm({"image": "2", "instance": "2"})
        >>> dataset_1 = Dataset({"path": {"1": ""}})
        >>> dataset_2 = Datasets([{"path": {"2": ""}})
        >>> experiments = Versions([dataset_1, dataset_2]) * Versions(
        ...     [algorithm_1, algorithm_2]
        ... )
        >>> assert experiments == Experiments(
        ...     [
        ...         Experiment.from_nodes(algorithm_1, dataset_1),
        ...         Experiment.from_nodes(algorithm_2, dataset_1),
        ...         Experiment.from_nodes(algorithm_1, dataset_2),
        ...         Experiment.from_nodes(algorithm_2, dataset_2),
        ...     ]
        ... )
        True
        """
        # multiply all children in self with all children in other
        # and flatten the resulting list of Experiments into a
        # single Experiments object.
        # i.e.
        # Versions([algorithm_1, algorithm_2]) * Versions([dataset_1, dataset_2])
        # first becomes a list of Experiments
        # [
        #   Experiments([Experiment.from_nodes(algorithm_1, dataset_1)]),
        #   Experiments([Experiment.from_nodes(algorithm_2, dataset_1)]),
        #   Experiments([Experiment.from_nodes(algorithm_1, dataset_2)]),
        #   Experiments([Experiment.from_nodes(algorithm_2, dataset_2)]),
        # ]
        # Which we then flatten to a single experiments object via chain
        # Experiments([
        #   Experiment.from_nodes(algorithm_1, dataset_1),
        #   Experiment.from_nodes(algorithm_2, dataset_1),
        #   Experiment.from_nodes(algorithm_1, dataset_2),
        #   Experiment.from_nodes(algorithm_2, dataset_2),
        # ])
        return Experiments(
            list(
                chain.from_iterable(
                    map(lambda item: item[0] * item[1], product(self, other))
                )
            )
        )


@singledispatch
def recursive_apply(node, fn: Callable) -> Any:
    """
    Applies a function to `dict` nodes in a JSON-like structure.
    The node that the function is applied to will be replaced with what
    `fn` returns. If the `fn` generates `runtool.datatypes.Versions`
    objects are merged into a new `runtool.datatypes.Versions` object
    and returned.

    NOTE::
        `runtool.datatypes.Versions` represents different versions of an object.

    In the following examples we will transform a JSON structure using
    the `transform` function defined below.

    >>> def transform(node):
    ...     '''
    ...     Converts node to a version object or multiplies it by 2
    ...     '''
    ...     if "version" in node:
    ...         return Versions(node["version"])
    ...     if "double" in node:
    ...         return 2 * node["double"]
    ...     return node

    Below is a simple example where the node is replaced with 2 after `transform`
    is applied to it.

    >>> recursive_apply(
    ...     {"double": 1},
    ...     fn=transform
    ... )
    2

    If the JSON structure contains nested nodes, `recursive_apply` applies `fn`
    to each `dict` node in the tree and replaces the node with whatever `fn` returns.

    >>> recursive_apply(
    ...     {
    ...         "no_double": 2,
    ...         "double_this": {
    ...             "double": 2
    ...         },
    ...     },
    ...     fn=transform
    ... )
    {'no_double': 2, 'double_this': 4}

    In the below example two `runtool.datatypes.Versions` will be created by
    the `transform` function. `recursive_apply` merges these and thus the result
    of `recursive_apply` will here be a `runtool.datatypes.Versions` object.

    >>> result = recursive_apply(
    ...     {
    ...         "my_list": [
    ...             {"hello": "there"},
    ...             {"a": {"version": [1, 2]}},
    ...             {"b": {"version": [3, 4]}},
    ...         ]
    ...     },
    ...     fn=transform
    ... )
    >>> type(result)
    <class 'runtool.recurse_config.Versions'>
    >>> for version in result:
    ...     print(version)
    {'my_list': [{'hello': 'there'}, {'a': 1}, {'b': 3}]}
    {'my_list': [{'hello': 'there'}, {'a': 1}, {'b': 4}]}
    {'my_list': [{'hello': 'there'}, {'a': 2}, {'b': 3}]}
    {'my_list': [{'hello': 'there'}, {'a': 2}, {'b': 4}]}

    Parameters
    ----------
    node
        The node which should be processed.
    fn
        The function which should be applied to the node.
    Returns
    -------
    Any
        Depends on how `fn` transforms the node.
    """
    return node


@recursive_apply.register
def recursive_apply_dict(node: dict, fn: Callable) -> Any:
    """
    Applies `fn` to the node, if `fn` changes the node,
    the changes should be returned. If the `fn` does not change the node,
    it calls `recursive_apply` on the children of the node.

    In case the recursion on the children results in one or more
    `runtool.datatypes.Versions` objects, the cartesian product of these
    versions is calculated and a new `runtool.datatypes.Versions` object will be
    returned containing the different versions of this node.

    """

    # else merge children of type Versions into a new Versions object
    expanded_children = []
    new_node = {}
    for key, value in node.items():
        child = recursive_apply(value, fn)
        # If the child is a Versions object, map the key to all its versions,
        # child = Versions([1,2]),
        # key = ['a']
        # ->
        # (('a':1), ('a':2))
        if isinstance(child, Versions):
            expanded_children.append(itertools.product([key], child))
        else:
            new_node[key] = child
    if expanded_children:
        # example:
        # expanded_children = [(('a':1), ('a':2)), (('b':1), ('b':2))]
        # new_node = {"c": 3}
        # results in:
        # [
        #   {'a':1, 'b':1, 'c':3},
        #   {'a':1, 'b':2, 'c':3},
        #   {'a':2, 'b':1, 'c':3},
        #   {'a':3, 'b':2, 'c':3},
        # ]
        new_node = [
            fn(
                dict(version_of_node, **new_node)
            )  # apply fn to the new version of the node
            for version_of_node in itertools.product(*expanded_children)
        ]

        # if the current node generated Versions object, these
        # need to be flattened as well. For example:
        # new_node = [Versions([1,2]), Versions([3,4])]
        # results in
        # Versions([[1,3], [1,4], [2,3], [2,4]])
        if all(isinstance(val, Versions) for val in new_node):
            return Versions(list(*itertools.product(*new_node)))
        return Versions(new_node)
    return fn(new_node)


@recursive_apply.register
def recursive_apply_list(node: list, fn: Callable) -> Any:
    """
    Calls `recursive_apply` on each element in the node, without applying `fn`.
    Calculates the cartesian product of any `runtool.datatypes.Versions` objects
    in the nodes children. From this a new `runtool.datatypes.Versions`object is
    generated representing the different variants that this node can take.

    NOTE::
        The indexes of the node are maintained throughout this process.
    """
    versions_in_children = []
    child_normal = [None] * len(node)  # maintans indexes
    for index, value in enumerate(node):
        child = recursive_apply(value, fn)
        if isinstance(child, Versions):
            # child = Versions([1,2])
            # ->
            # expanded_child_version = ((index, 1), (index, 2))
            expanded_child_version = itertools.product([index], child)
            versions_in_children.append(expanded_child_version)
        else:
            child_normal[index] = child

    if not versions_in_children:
        return child_normal

    # merge the data from the children which were not Versions objects
    # together with the data from the children which were Versions objects
    new_versions = []
    for version in itertools.product(*versions_in_children):
        new_data = child_normal[:]
        for index, value in version:
            new_data[index] = value
        new_versions.append(new_data)

    return Versions(new_versions)
