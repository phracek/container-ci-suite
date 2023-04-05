# MIT License
#
# Copyright (c) 2018-2019 Red Hat, Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import pytest
from flexmock import flexmock

from container_ci_suite.helm import HelmChartsAPI


class TestContainerCISuiteHelmCharts:

    def setup_method(self):
        self.helm_chart = HelmChartsAPI("foo_path", "postgresql-imagestreams", "0.0.1", namespace="pgsql-13")

    def test_helm_api(self):
        assert self.helm_chart.path == "foo_path"
        assert self.helm_chart.package_name == "postgresql-imagestreams"
        assert self.helm_chart.version == "0.0.1"
        assert self.helm_chart.namespace == "pgsql-13"

    @pytest.mark.parametrize(
        "tag,registry,expected_value",
        [
            ("13-el9", "registry.redhat.io/rhel9/postgresql-13:latest", True),
            ("13-el8", "registry.redhat.io/rhel8/postgresql-13:latest", True),
            ("13-el6", "registry.redhat.io/rhel8/postgresql-13:latest", False),
            ("13-el8", "registry.redhat.io/rhel7/postgresql-13:latest", False),
        ]
    )
    def test_check_imagestreams(self, tag, registry, expected_value, postgresql_json):
        flexmock(HelmChartsAPI).should_receive("get_is_json").and_return(postgresql_json)
        self.helm_chart.tag = tag
        assert self.helm_chart.check_imagestreams(tag, registry=registry) == expected_value

    def test_package_helm_chart_success(self, helm_package_success):
        flexmock(HelmChartsAPI).should_receive("run_helm_command").and_return(helm_package_success)
        assert self.helm_chart.helm_package()

    def test_package_helm_chart_failed(self, helm_package_failed):
        flexmock(HelmChartsAPI).should_receive("run_helm_command").and_return(helm_package_failed)
        assert not self.helm_chart.helm_package()

    @pytest.mark.parametrize(
        "list_output,expected_output",
        [
            (True, True),
            (False, False),
        ]
    )
    def test_package_installation_success(
            self, package_installation_json, helm_list_json, list_output, expected_output
    ):
        flexmock(HelmChartsAPI).should_receive("get_helm_json_output").and_return(package_installation_json)
        flexmock(HelmChartsAPI).should_receive("check_helm_installation").and_return(list_output)
        assert self.helm_chart.helm_installation() == expected_output