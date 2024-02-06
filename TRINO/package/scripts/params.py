# -*- coding: utf-8 -*-
# !/usr/bin/env python
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
import random
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.version import get_major_version
from resource_management.libraries.functions.version import format_stack_version

########################################## System Env ##########################################
config = Script.get_config()
# java64_home = config["ambariLevelParams"]["java_home"]
hostname = config['agentLevelParams']['hostname']

stack_version_unformatted = config['clusterLevelParams']['stack_version']
stack_version_formatted_major = format_stack_version(stack_version_unformatted)
major_stack_version = get_major_version(stack_version_formatted_major)


# local hdp cluster hive metastore uri
hiveMetaStoreUri = str(config['configurations']['hive-site']['hive.metastore.uris'])
HIVE_METASTORE_URI = "thrift://localhost:9083"
if hiveMetaStoreUri:
    if ',' in hiveMetaStoreUri:
        HIVE_METASTORE_URI = hiveMetaStoreUri.split(',')[0].strip()
    else:
        HIVE_METASTORE_URI = hiveMetaStoreUri

# generate uuid
def generate_random_string(length, number):
    # 设置随机种子
    random.seed("hdp-trino-random-seed-{0}-{1}".format(number, hostname))
    letters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(random.choice(letters) for i in range(length))


def generate_uuid():
    return '{0}-{1}-{2}-{3}-{4}'.format(generate_random_string(8, 1),
                                        generate_random_string(4, 2),
                                        generate_random_string(4, 3),
                                        generate_random_string(4, 4),
                                        generate_random_string(12, 5))

########################################## env-trino ##########################################
# java and trino cli install package download url
java_download_url = config['configurations']['trino-env.sh.conf']['java_download_url']
trino_cli_download_url = config['configurations']['trino-env.sh.conf']['trino_cli_download_url']
trino_base_path = "/usr/hdp/{0}/trino".format(major_stack_version)

# trino user and group
trino_user = config['configurations']['trino-env.sh.conf']['trino_user']
trino_group = config['configurations']['trino-env.sh.conf']['trino_group']

########################################## node.properties ##########################################
# trino cluster env name
node_uuid = generate_uuid()
node_environment = str(config['configurations']['trino-node.properties']['node.environment']).lower()
node_data_dir = config['configurations']['trino-node.properties']['node.data-dir']
catalog_config_dir = config['configurations']['trino-node.properties']['catalog.config-dir']
node_server_log_file = config['configurations']['trino-node.properties']['node.server-log-file']
node_launcher_olog_file = config['configurations']['trino-node.properties']['node.launcher-log-file']

########################################## config.properties ##########################################
coordinator = 'false'
http_server_http_port = config['configurations']['trino-config.properties']['http-server.http.port']
discovery_uri = config['configurations']['trino-config.properties']['discovery.uri']
http_server_log_path = config['configurations']['trino-config.properties']['http-server.log.path']

node_scheduler_include_coordinator = str(config['configurations']['trino-config.properties']['node-scheduler.include-coordinator']).lower()
node_scheduler_max_splits_per_node = config['configurations']['trino-config.properties']['node-scheduler.max-splits-per-node']
node_scheduler_min_pending_splits_per_task = config['configurations']['trino-config.properties']['node-scheduler.min-pending-splits-per-task']
node_scheduler_max_adjusted_pending_splits_per_task = config['configurations']['trino-config.properties']['node-scheduler.max-adjusted-pending-splits-per-task']
node_scheduler_max_unacknowledged_splits_per_task = config['configurations']['trino-config.properties']['node-scheduler.max-unacknowledged-splits-per-task']
node_scheduler_min_candidates = config['configurations']['trino-config.properties']['node-scheduler.min-candidates']
node_scheduler_policy = str(config['configurations']['trino-config.properties']['node-scheduler.policy']).lower()

retry_policy = str(config['configurations']['trino-config.properties']['retry-policy']).upper()
exchange_deduplication_buffer_size = config['configurations']['trino-config.properties']['exchange.deduplication-buffer-size']
fault_tolerant_execution_exchange_encryption_enabled = str(config['configurations']['trino-config.properties']['fault-tolerant-execution.exchange-encryption-enabled']).lower()
# query params
query_max_cpu_time = config['configurations']['trino-config.properties']['query.max-cpu-time']
query_max_memory = config['configurations']['trino-config.properties']['query.max-memory']
query_client_timeout = config['configurations']['trino-config.properties']['query.client.timeout']
query_execution_policy = str(config['configurations']['trino-config.properties']['query.execution-policy']).lower()
query_low_memory_killer_policy = str(config['configurations']['trino-config.properties']['query.low-memory-killer.policy']).lower()
task_low_memory_killer_policy = str(config['configurations']['trino-config.properties']['task.low-memory-killer.policy']).lower()
query_low_memory_killer_delay = str(config['configurations']['trino-config.properties']['query.low-memory-killer.delay']).lower()
query_max_execution_time = config['configurations']['trino-config.properties']['query.max-execution-time']
query_max_length = config['configurations']['trino-config.properties']['query.max-length']
query_max_run_time = config['configurations']['trino-config.properties']['query.max-run-time']
query_max_stage_count = config['configurations']['trino-config.properties']['query.max-stage-count']
query_max_history = config['configurations']['trino-config.properties']['query.max-history']
query_min_expire_age = config['configurations']['trino-config.properties']['query.min-expire-age']
query_remote_task_max_error_duration = config['configurations']['trino-config.properties']['query.remote-task.max-error-duration']
# spill params
spill_enabled = str(config['configurations']['trino-config.properties']['spill-enabled']).lower()
spiller_spill_path = config['configurations']['trino-config.properties']['spiller-spill-path']
spiller_max_used_space_threshold = config['configurations']['trino-config.properties']['spiller-max-used-space-threshold']
spiller_threads = config['configurations']['trino-config.properties']['spiller-threads']
max_spill_per_node = config['configurations']['trino-config.properties']['max-spill-per-node']
query_max_spill_per_node = config['configurations']['trino-config.properties']['query-max-spill-per-node']
aggregation_operator_unspill_memory_limit = config['configurations']['trino-config.properties']['aggregation-operator-unspill-memory-limit']
spill_encryption_enabled = str(config['configurations']['trino-config.properties']['spill-encryption-enabled']).lower()
# exchange params
exchange_client_threads = config['configurations']['trino-config.properties']['exchange.client-threads']
exchange_concurrent_request_multiplier = config['configurations']['trino-config.properties']['exchange.concurrent-request-multiplier']
exchange_data_integrity_verification = str(config['configurations']['trino-config.properties']['exchange.data-integrity-verification']).upper()
exchange_max_buffer_size = config['configurations']['trino-config.properties']['exchange.max-buffer-size']
exchange_max_response_size = config['configurations']['trino-config.properties']['exchange.max-response-size']
sink_max_buffer_size = config['configurations']['trino-config.properties']['sink.max-buffer-size']
sink_max_broadcast_buffer_size = config['configurations']['trino-config.properties']['sink.max-broadcast-buffer-size']
# task params
task_http_response_threads = config['configurations']['trino-config.properties']['task.http-response-threads']
task_http_timeout_threads = config['configurations']['trino-config.properties']['task.http-timeout-threads']
task_info_update_interval = config['configurations']['trino-config.properties']['task.info-update-interval']
task_max_drivers_per_task = config['configurations']['trino-config.properties']['task.max-drivers-per-task']
task_max_partial_aggregation_memory = config['configurations']['trino-config.properties']['task.max-partial-aggregation-memory']
task_min_drivers_per_task = config['configurations']['trino-config.properties']['task.min-drivers-per-task']

########################################## jvm.config ##########################################
jvm_config = config['configurations']['trino-jvm.config']['content']

########################################## env.sh && log.properties ##########################################
env_sh = config['configurations']['trino-env.sh']['content']
log_properties = config['configurations']['trino-log.properties']['content']

########################################## trino connectors ##########################################
connectors_to_add = config['configurations']['trino-connectors.properties']['connectors.to.add']
connectors_to_delete = config['configurations']['trino-connectors.properties']['connectors.to.delete']

########################################## resource-groups ##########################################
resource_groups_json = config['configurations']['trino-resource-groups.json']['content']
resource_groups_properties = config['configurations']['trino-resource-groups.properties']['content']
session_property_config_json = config['configurations']['trino-session-property-config.json']['content']
session_property_config_properties = config['configurations']['trino-session-property-config.properties']['content']

########################################## event-listener ##########################################
enable_event_listener = str(config['configurations']['trino-event-listener.properties']['enable.event-listener']).lower()
event_listener_properties = config['configurations']['trino-event-listener.properties']['content']


