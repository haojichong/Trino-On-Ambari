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


class Coordinator(Script):
    def install(self, env):
        import common
        common.install_trino()
        self.configure(env)

    def configure(self, env):
        import common, params
        params.coordinator = 'true'
        common.trino_configure(env, True)

    def start(self, env):
        import common
        self.configure(env)
        Execute(common.exportJavaHomeAndPath + ' && {0} start'.format(common.launcherPath))

    def stop(self, env):
        import common
        Execute(common.exportJavaHomeAndPath + ' && {0} stop'.format(common.launcherPath))

    def status(self, env):
        import common
        try:
            Execute(common.exportJavaHomeAndPath + ' && {0} status'.format(common.launcherPath))
        except ExecutionFailed as ef:
            if ef.code == 3:
                raise ComponentIsNotRunning("ComponentIsNotRunning")
            else:
                raise ef


if __name__ == '__main__':
    Coordinator().execute()
