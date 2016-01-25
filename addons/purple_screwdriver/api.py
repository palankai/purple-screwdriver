import collections


ModuleState = collections.namedtuple(
    'ModuleState', ['name', 'state', 'is_outdated']
)
ModuleConfig = collections.namedtuple(
    'ModuleCondig', ['name', 'state']
)
Action = collections.namedtuple(
    'Action', ['name', 'action']
)


def get_version(release, module):
    if module is False or module == 'absent':
        return module
    if module.count('.') >= 2:
        return module
    return '%s.%s' % (release, module)


class ActionPlanBuilder(object):

    def __init__(self, system, expected):
        self.system = system
        self.expected = expected

    def build(self):
        actions = []

        for exp in self.expected.values():
            if(
                self.system[exp.name].state == 'uninstalled' and
                exp.state == 'uninstalled'
            ):
                continue
            if(
                self.system[exp.name].state == 'installed' and
                exp.state == 'uninstalled'
            ):
                actions.append(Action(exp.name, 'to remove'))
                continue
            if(
                self.system[exp.name].state == 'uninstalled' and
                exp.state == 'installed'
            ):
                actions.append(Action(exp.name, 'to install'))
                continue
            if(
                self.system[exp.name].state == 'installed' and
                exp.state == 'installed'
            ):
                if self.system[exp.name].is_outdated:
                    actions.append(Action(exp.name, 'to upgrade'))
                continue
            if exp.state == 'upgraded':
                installed = self.system[exp.name].state == 'installed'
                if installed:
                    actions.append(Action(exp.name, 'to upgrade'))
                else:
                    actions.append(Action(exp.name, 'to install'))
                continue
            raise ValueError('Invalid value of %s: %s' % (exp.name, exp.state))
        return actions
