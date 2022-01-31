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

from typing import Optional

import boto3

# TODO: we could use it from gluon-ts, but this would add a major dependency
from smily.util.settings import Settings, Dependency
from smily.util.aws_config import Config


def sagemaker_client(boto_session, endpoint):
    return boto_session.client("sagemaker")


def logs_client(boto_session):
    return boto_session.client("logs")


class Env(Settings):
    boto_session: boto3.Session
    sagemaker: Dependency = sagemaker_client
    cw_logs: Dependency = logs_client
    endpoint: Optional[str] = None

    aws_config: Config = Config.read()


env = Env()
