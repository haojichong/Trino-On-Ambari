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

import ast
import grp
import pwd
import sys
import os
import params
from resource_management import *
from resource_management import User, Group, Logger
from resource_management.core.resources.system import Execute

# Install Path
TRINO_BASE_PATH = params.trino_base_path
# Config Path
TRINO_ETC_PATH = "/etc/trino"
# Java 17 Path
JAVA17_HOME = TRINO_BASE_PATH + "/java17"
# Bin Path
TRINO_BIN_PATH = TRINO_BASE_PATH + "/bin"
# CataLog Path
TRINO_CATALOG_PATH = TRINO_ETC_PATH + "/catalog"
# Java And TrinoCli Download Path
JAVA_DOWNLOAD_URL = params.java_download_url
TRINO_CLI_DOWNLOAD_URL = params.trino_cli_download_url
# Export Env Path
exportJavaHomeAndPath = 'export JAVA_HOME=' + JAVA17_HOME + ' && export PATH=${JAVA_HOME}/bin:$PATH '
exportJavaHomePath = 'export JAVA_HOME=' + JAVA17_HOME
exportPath = 'export PATH=${JAVA_HOME}/bin:$PATH '
# launcher.sh script path
launcherPath = TRINO_BIN_PATH + '/launcher'


# Install Trino and Java 17
def install_trino():
    # install htpasswd command
    # Execute('yum install -y httpd')
    Execute('yum install -y wget', user='root', ignore_failures=True)

    # create user and group
    createUserIfNotExist("trino", "trino")
    if not os.path.exists(JAVA17_HOME):
        # mkdir java base path
        Execute('mkdir -p {0}'.format(JAVA17_HOME))
        # download java tar package
        Execute('cd {0};wget {1} -O java17.tar.gz'.format(JAVA17_HOME, JAVA_DOWNLOAD_URL))
        # decompressing a tar package
        Execute('cd {0};tar -xf java17.tar.gz --strip-components=1'.format(JAVA17_HOME))
        # remove java17 tar package
        Execute('rm -rfv {0}/java17.tar.gz'.format(JAVA17_HOME))
    # export env (java 17) && yum install
    Execute('{0} && yum install -y --skip-broken trino-server-rpm*'.format(exportJavaHomeAndPath))
    # mkdir catalog dir
    Execute('mkdir -p {0}'.format(TRINO_CATALOG_PATH))


# Create User and Group
def createUserIfNotExist(user, group):
    try:
        grp.getgrnam(group)
    except KeyError:
        Group("trino", group_name=group)

    try:
        pwd.getpwnam(user)
    except Exception:
        Logger.info("User: %s not existed, create it" % user)
        User("trino", username=user,
             gid=group,
             groups=[group], ignore_failures=True)
        Logger.info("User: %s create successful" % user)


# Custom Config
def customConf(path, dic):
    dic_copy = dic.copy()
    with open(path, "r+") as fr:
        lines = fr.readlines()
        for line in lines:
            for key in dic:
                if line.startswith(key):
                    del dic_copy[key]

    with open(path, "a+") as fw:
        fw.write(
            "\n# ========================================= Custom Config =========================================\n")
        for key in dic_copy:
            line = '#\n' + (key + "=" + dic_copy[key] + "\n")
            fw.write(line)


def trino_configure(env, isCoordinator=False):
    import params
    env.set_params(params)

    # config.properties file
    config_properties = params.config['configurations']['trino-config.properties']
    File("{0}/config.properties".format(TRINO_ETC_PATH),
         content=Template("config.properties.j2",
                          configurations=config_properties)
         )

    # custom conf
    customConf("{0}/config.properties".format(TRINO_ETC_PATH), config_properties)

    # node.properties file
    node_properties = params.config['configurations']['trino-node.properties']
    File("{0}/node.properties".format(TRINO_ETC_PATH),
         content=Template("node.properties.j2",
                          configurations=node_properties)
         )

    # custom conf
    customConf("{0}/node.properties".format(TRINO_ETC_PATH), node_properties)

    # jvm.config file
    jvm_config_content = InlineTemplate(format(params.jvm_config))
    File("{0}/jvm.config".format(TRINO_ETC_PATH),
         content=jvm_config_content)

    # env.sh file
    env_sh_content = InlineTemplate(format(params.env_sh))
    File("{0}/env.sh".format(TRINO_ETC_PATH),
         content=env_sh_content)

    # set log conf
    log_content = InlineTemplate(format(params.log_properties))
    File("{0}/log.properties".format(TRINO_ETC_PATH),
         content=log_content)

    connectorAddContent = params.connectors_to_add.replace('{{{HIVE_METASTORE_URI}}}', params.HIVE_METASTORE_URI)
    Execute("mkdir -p /data/trino/hive-cache")

    # set connectors
    create_connectors(connectorAddContent)
    delete_connectors(params.connectors_to_delete)
    create_connectors("{'tpch': ['connector.name=tpch']}")

    if os.path.exists("/etc/trino/catalog/hive.properties") \
            and os.path.exists("/usr/hdp/{0}/hadoop/lib/lzo-hadoop-1.0.5.jar".format(params.major_stack_version)) \
            and not os.path.exists("{0}/plugin/hive/lzo-hadoop-1.0.5.jar".format(TRINO_BASE_PATH)):
        Execute('ln -s /usr/hdp/{0}/hadoop/lib/lzo-hadoop-1.0.5.jar {1}/plugin/hive'.format(params.major_stack_version,
                                                                                            TRINO_BASE_PATH))

    if isCoordinator:
        # resource-groups.json file
        resource_groups_json_content = params.resource_groups_json
        File("{0}/resource-groups.json".format(TRINO_ETC_PATH),
             content=resource_groups_json_content)
        # resource-groups.properties file
        resource_groups_properties_content = InlineTemplate(format(params.resource_groups_properties))
        File("{0}/resource-groups.properties".format(TRINO_ETC_PATH),
             content=resource_groups_properties_content)
        # session-property-config.jsonfile
        session_property_config_json_content = params.session_property_config_json
        File("{0}/session-property-config.json".format(TRINO_ETC_PATH),
             content=session_property_config_json_content)
        # session-property-config.properties file
        session_property_config_properties_content = InlineTemplate(format(params.session_property_config_properties))
        File("{0}/session-property-config.properties".format(TRINO_ETC_PATH),
             content=session_property_config_properties_content)
        # event-listener.properties file
        event_listener_properties_centent = InlineTemplate(format(params.event_listener_properties))
        File("{0}/event-listener.properties".format(TRINO_ETC_PATH),
             content=event_listener_properties_centent)
        try:
            if params.enable_event_listener == 'true':
                Execute(
                    'mv {0}/event-listener.properties.template {0}/event-listener.properties'.format(TRINO_ETC_PATH))
            else:
                Execute(
                    'mv {0}/event-listener.properties {0}/event-listener.properties.template'.format(TRINO_ETC_PATH))
        except Exception:
            Logger.warning("Failed to configure the event listener. The file does not exist.")


def create_connectors(connectors_to_add):
    if not connectors_to_add:
        return
    connectors_dict = ast.literal_eval(connectors_to_add)
    for connector in connectors_dict:
        connector_file = os.path.join(TRINO_CATALOG_PATH, connector + '.properties')
        with open(connector_file, 'w') as f:
            for lineitem in connectors_dict[connector]:
                f.write('{0}\n'.format(lineitem))


def delete_connectors(connectors_to_delete):
    if not connectors_to_delete:
        return
    connectors_list = ast.literal_eval(connectors_to_delete)
    for connector in connectors_list:
        connector_file_name = os.path.join(TRINO_CATALOG_PATH, connector + '.properties')
        Execute('rm -f {0}'.format(connector_file_name))
