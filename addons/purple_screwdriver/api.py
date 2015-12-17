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
