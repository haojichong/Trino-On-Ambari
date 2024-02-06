# -*- coding: utf-8 -*-
# !/usr/bin/env ambari-python-wrap
"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# Python imports
import imp
import os
import traceback
import re
import socket
import fnmatch
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STACKS_DIR = os.path.join(SCRIPT_DIR, '../../../../../stacks/')
PARENT_FILE = os.path.join(STACKS_DIR, 'service_advisor.py')

try:
    if "BASE_SERVICE_ADVISOR" in os.environ:
        PARENT_FILE = os.environ["BASE_SERVICE_ADVISOR"]
    with open(PARENT_FILE, 'rb') as fp:
        service_advisor = imp.load_module('service_advisor', fp, PARENT_FILE, ('.py', 'rb', imp.PY_SOURCE))
except Exception as e:
    traceback.print_exc()
    print
    "Failed to load parent"


class TrinoServiceAdvisor(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(TrinoServiceAdvisor, self)
        self.as_super.__init__(*args, **kwargs)
        self.initialize_logger("TrinoServiceAdvisor")
        # Always call these methods
        self.modifyMastersWithMultipleInstances()
        self.modifyCardinalitiesDict()
        self.modifyHeapSizeProperties()
        self.modifyNotValuableComponents()
        self.modifyComponentsNotPreferableOnServer()
        self.modifyComponentLayoutSchemes()

    def modifyMastersWithMultipleInstances(self):
        pass

    def modifyCardinalitiesDict(self):
        pass

    def modifyHeapSizeProperties(self):
        pass

    def modifyNotValuableComponents(self):
        pass

    def modifyComponentsNotPreferableOnServer(self):
        pass

    def modifyComponentLayoutSchemes(self):
        pass

    def getServiceComponentLayoutValidations(self, services, hosts):
        return self.getServiceComponentCardinalityValidations(services, hosts, "Trino")

    def getServiceConfigurationRecommendations(self, configurations, clusterData, services, hosts):
        self.logger.info("Class: %s, Method: %s. Recommending Service Configurations." %
                         (self.__class__.__name__, inspect.stack()[0][3]))
        recommender = TrinoRecommender()
        recommender.recommendTrinoConfigurationsFromHDP(configurations, clusterData, services, hosts)

    def getServiceConfigurationsValidationItems(self, configurations, recommendedDefaults, services, hosts):
        self.logger.info("Class: %s, Method: %s. Validating Configurations." %
                         (self.__class__.__name__, inspect.stack()[0][3]))
        validator = TrinoValidator()
        return validator.validateListOfConfigUsingMethod(configurations, recommendedDefaults, services, hosts,
                                                         validator.validators)


class TrinoRecommender(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(TrinoRecommender, self)
        self.as_super.__init__(*args, **kwargs)

    def recommendTrinoConfigurationsFromHDP(self, configurations, clusterData, services, hosts):
        # Automatically obtains and recommends the IP address of a Trino Coordinator node
        putTrinoSiteProperty = self.putProperty(configurations, "trino-config.properties", services)
        trinoCoordinatorHost = self.getHostWithComponent("TRINO", "TRINO_COORDINATOR", services, hosts)
        if trinoCoordinatorHost is not None and len(trinoCoordinatorHost) > 0:
            putTrinoSiteProperty("discovery.uri",
                                 "http://" + trinoCoordinatorHost["Hosts"]["host_name"] + ":8285")


class TrinoValidator(service_advisor.ServiceAdvisor):
    def __init__(self, *args, **kwargs):
        self.as_super = super(TrinoValidator, self)
        self.as_super.__init__(*args, **kwargs)
        self.validators = []
