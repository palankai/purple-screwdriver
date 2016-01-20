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


def get_action(name, expected_version, available_version, installed_version, state):
    # When have to remove
    if(
        expected_version == 'absent' and
        state in ['installed', 'to install', 'to upgrade']
    ):
        return 'to remove'
    # When have to install
    if(
        expected_version == available_version and
        state in ['uninstalled']
    ):
        return 'to install'
    # When have to upgrade
    if(
        expected_version == available_version > installed_version and
        state in ['installed']
    ):
        return 'to upgrade'

    # When don't have to anything
    if(
        expected_version == available_version > installed_version and
        state in ['to upgrade']
    ):
        return False
    if(
        expected_version == 'absent' and
        state in ['to remove', 'uninstalled']
    ):
        return False
    if(
        expected_version == available_version == installed_version and
        state in ['installed']
    ):
        return False

    # When the expectation is impossible
    if expected_version != 'absent' and expected_version != available_version:
        raise Exception("%s: %s!=%s" % (name, expected_version, available_version))


def get_version(release, module):
    if module is False or module == 'absent':
        return module
    if module.count('.') >= 2:
        return module
    return '%s.%s' % (release, module)


class ActionPlanBuilder(object):

    def __init__(self, system, stored, expected):
        self.system = system
        self.stored = stored
        self.expected = expected
        pass

    def build(self):
        actions = []

        for mod in self.stored:
            if mod not in self.expected:
                actions.append(Action(mod, 'to remove'))

        for exp in self.expected.values():
            if(
                self.system[exp.name].state == 'uninstalled'
                and exp.state == 'installed'
            ):
                actions.append(Action(exp.name, 'to install'))
                continue
            if(
                self.system[exp.name].state == 'installed'
                and exp.state == 'installed'
                and self.system[exp.name].is_outdated
            ):
                actions.append(Action(exp.name, 'to update'))
                continue
            if exp.state == 'updated':
                installed = self.system[exp.name].state == 'installed'
                if installed:
                    actions.append(Action(exp.name, 'to update'))
                else:
                    actions.append(Action(exp.name, 'to install'))
                continue
        return actions
