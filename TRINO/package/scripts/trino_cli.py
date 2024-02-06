# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from resource_management import *
import os


class Cli(Script):
    def install(self, env):
        import common
        # Execute('yum install -y wget'.format())
        if os.path.exists('/usr/bin/trino-cli'):
            Logger.info('trino client installed')
        else:
            Logger.info('start install trino client')
            Execute('rm -rf {0}/trino-cli'.format(common.TRINO_BIN_PATH))
            Execute('mkdir -p {0}'.format(common.TRINO_BIN_PATH))
            Execute('wget {0} -O {1}/trino-cli'.format(common.TRINO_CLI_DOWNLOAD_URL, common.TRINO_BIN_PATH))
            Execute('chmod +x {0}/trino-cli'.format(common.TRINO_BIN_PATH))
            # soft connect to the system directory
            Execute('ln -s {0}/trino-cli /usr/bin/'.format(common.TRINO_BIN_PATH))

    def status(self, env):
        raise ClientComponentHasNoStatus()

    def configure(self, env):
        import params
        env.set_params(params)

    def start(self, env):
        import params
        env.set_params(params)

    def stop(self, env):
        import params
        env.set_params(params)


if __name__ == '__main__':
    Cli().execute()
