#  Copyright (c) 2015-2017 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import collections

import ansible
import ansible.inventory
import ansible.vars
import ansible.executor.task_queue_manager
import ansible.parsing.dataloader
import ansible.playbook.play
import ansible.plugins.callback

from molecule import util


class ResultCallback(ansible.plugins.callback.CallbackBase):
    def __init__(self, config):
        self._config = config

    def v2_runner_on_ok(self, result, **kwargs):
        print self._config.config
        print result._result

    def v2_runner_on_failed(self, result, ignore_errors=False):
        print result._result['msg']


Options = collections.namedtuple('Options', [
    'connection', 'module_path', 'forks', 'become', 'become_method',
    'become_user', 'check'
])


class AnsibleExec():
    def __init__(self, config):
        self.variable_manager = ansible.vars.VariableManager()
        self.loader = ansible.parsing.dataloader.DataLoader()
        self.options = Options(
            connection='local',
            module_path='/path/to/mymodules',
            forks=100,
            become=None,
            become_method=None,
            become_user=None,
            check=False)

        self.passwords = {'vault_pass': 'secret'}
        self.results_callback = ResultCallback(config)
        self.inventory = ansible.inventory.Inventory(
            loader=self.loader,
            variable_manager=self.variable_manager,
            host_list=config.provisioner.inventory_file)
        self.variable_manager.set_inventory(self.inventory)

    def execute_task(self, task):
        pd = {
            'name': "Molecule's Ansible playbook executor",
            'hosts': "localhost",
            'gather_facts': 'no',
            'tasks': [task]
        }

        play = ansible.playbook.play.Play().load(
            pd, variable_manager=self.variable_manager, loader=self.loader)

        tqm = None
        try:
            tqm = ansible.executor.task_queue_manager.TaskQueueManager(
                inventory=self.inventory,
                variable_manager=self.variable_manager,
                loader=self.loader,
                options=self.options,
                passwords=self.passwords,
                stdout_callback=self.results_callback)
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def execute_module(self, module, **kwargs):
        task = dict(action=dict(module=module, args=dict(kwargs)))
        self.execute_task(task)
