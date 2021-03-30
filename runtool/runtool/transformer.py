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

from functools import partial

from runtool.recurse_config import recursive_apply, Versions
from runtool.transformations import (
    apply_eval,
    apply_from,
    apply_ref,
    apply_trial,
    apply_each,
)


def apply_transformations(data: dict) -> list:
    """
    Applies a chain of transformations converting nodes in `data` using

    - `apply_from`
    - `apply_eval`
    - `apply_each`
    - `apply_ref`

    Returns the different variants of the `data` after transformations as a list.

    >>> result = apply_transformations(
    ...    {
    ...         "base": {"msg": "hi"},
    ...         "a": {"$from": "base", "smth": {"$each": [{"$eval": "pow(7, 2)"}, 2]}},
    ...         "b": [{"$ref": "a.msg"}],
    ...     }
    ... )
    >>> for version in result:
    ...     print(version)
    {'a': {'smth': 49, 'msg': 'hi'}, 'base': {'msg': 'hi'}, 'b': ['hi']}
    {'a': {'smth': 2, 'msg': 'hi'}, 'base': {'msg': 'hi'}, 'b': ['hi']}

    Parameters
    ----------
    data
        The dictionary which should be transformed
    Returns
    -------
    list
        the transformed `data` where each item is a version of the data.
    """
    data = recursive_apply(data, partial(apply_from, context=data))
    data = recursive_apply(data, partial(apply_eval, locals=data))
    data = recursive_apply(data, apply_each)

    data = list(data) if isinstance(data, Versions) else [data]
    data = [
        recursive_apply(item, partial(apply_ref, context=item))
        for item in data
    ]
    return data
