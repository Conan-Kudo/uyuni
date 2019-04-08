# coding: utf-8
"""
Test activation key methods.
"""
from mock import MagicMock, patch
import pytest
import time
import hashlib
import spacecmd.activationkey


@pytest.fixture
def shell():
    """
    Create fake shell.
    """
    base = MagicMock()
    base.session = hashlib.sha256(str(time.time()).encode("utf-8")).hexdigest()
    base.do_activationkey_list = MagicMock(return_value="do_activation_list")

    return base


class TestSCActivationKey:
    """
    Test activation key.
    """
    def test_completer_ak_addpackages(self, shell):
        """
        Test tab completer activation keys on addpackages.
        """
        print()
        text = "Communications satellite used by the military for star wars."
        completer = MagicMock()
        with patch("spacecmd.activationkey.tab_completer", completer):
            spacecmd.activationkey.complete_activationkey_addpackages(shell, text, "do this", None, None)
            assert completer.called
            call_id, ret_text = completer.call_args_list[0][0]
            assert call_id == "do_activation_list"
            assert ret_text == text


class TestSCActivationKeyMethods:
    """
    Test actuvation key methods.
    """
    def test_do_activationkey_addpackages_noargs(self, shell):
        """
        Test add packages method call shows help on no args.
        """
        shell.help_activationkey_addpackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addPackages = MagicMock()

        spacecmd.activationkey.do_activationkey_addpackages(shell, "")
        assert shell.help_activationkey_addpackages.called

    def test_do_activationkey_addpackages_help_args(self, shell):
        """
        Test add packages method call shows help on help args passed.
        """
        shell.help_activationkey_addpackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addPackages = MagicMock()

        spacecmd.activationkey.do_activationkey_addpackages(shell, "help")
        assert shell.help_activationkey_addpackages.called

    def test_do_activationkey_addpackages_args(self, shell):
        """
        Test add packages method call shows help on args passed.
        """
        shell.help_activationkey_addpackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addPackages = MagicMock()

        spacecmd.activationkey.do_activationkey_addpackages(shell, "call something here")
        assert not shell.help_activationkey_addpackages.called
        assert shell.client.activationkey.addPackages.called
        print()
        session, fun, args = shell.client.activationkey.addPackages.call_args_list[0][0]
        assert session == shell.session
        assert fun == "call"
        assert isinstance(args, list)
        assert len(args) == 2
        for arg in args:
            assert arg["name"] in ["something", "here"]

    def test_do_activationkey_removepackages_noargs(self, shell):
        """
        Test remove packages method call shows help on no args.
        """
        shell.help_activationkey_removepackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removePackages = MagicMock()

        # TODO: Add help for remove packages!
        spacecmd.activationkey.do_activationkey_removepackages(shell, "")
        assert not shell.help_activationkey_removePackages.called

    def test_do_activationkey_removepackages_help_args(self, shell):
        """
        Test remove packages method call shows help if only one argument is passed.
        """
        shell.help_activationkey_removepackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removePackages = MagicMock()

        spacecmd.activationkey.do_activationkey_removepackages(shell, "key")
        assert shell.help_activationkey_removepackages.called

    def test_do_activationkey_removepackages_args(self, shell):
        """
        Test remove packages method calls "removePackages" API call.
        """
        shell.help_activationkey_removepackages = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removePackages = MagicMock()

        spacecmd.activationkey.do_activationkey_removepackages(shell, "key package")
        assert not shell.help_activationkey_removepackages.called
        assert shell.client.activationkey.removePackages.called
        session, fun, args = shell.client.activationkey.removePackages.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert "name" in args[0]
        assert args[0]["name"] == "package"

    def test_do_activationkey_addgroups_noargs(self, shell):
        """
        Test addgroup without args calls help.
        """
        shell.help_activationkey_addgroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addServerGroups = MagicMock()

        spacecmd.activationkey.do_activationkey_addgroups(shell, "")
        assert shell.help_activationkey_addgroups.called

    def test_do_activationkey_addgroups_help_args(self, shell):
        """
        Test add groups method call shows help if only one argument is passed.
        """
        shell.help_activationkey_addgroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addServerGroups = MagicMock()

        spacecmd.activationkey.do_activationkey_addgroups(shell, "key")
        assert shell.help_activationkey_addgroups.called

    def test_do_activationkey_addgroups_args(self, shell):
        """
        Test "addgroups" method calls "addServerGroups" API call.
        """
        shell.help_activationkey_addgroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addServerGroups = MagicMock()
        shell.client.systemgroup.getDetails = MagicMock(return_value={"id": 42})

        spacecmd.activationkey.do_activationkey_addgroups(shell, "key group")
        assert not shell.help_activationkey_addgroups.called
        assert shell.client.activationkey.addServerGroups.called
        session, fun, args = shell.client.activationkey.addServerGroups.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == [42]

    def test_do_activationkey_removegroups_noargs(self, shell):
        """
        Test removegroup without args calls help.
        """
        shell.help_activationkey_removegroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeServerGroups = MagicMock()

        spacecmd.activationkey.do_activationkey_removegroups(shell, "")
        assert shell.help_activationkey_removegroups.called

    def test_do_activationkey_removegroups_help_args(self, shell):
        """
        Test remove groups method call shows help if only one argument is passed.
        """
        shell.help_activationkey_removegroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeServerGroups = MagicMock()

        spacecmd.activationkey.do_activationkey_removegroups(shell, "key")
        assert shell.help_activationkey_removegroups.called
        assert not shell.client.activationkey.removeServerGroups.called

    def test_do_activationkey_removegroups_args(self, shell):
        """
        Test "removegroups" method calls "removeServerGroups" API call.
        """
        shell.help_activationkey_removegroups = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeServerGroups = MagicMock()
        shell.client.systemgroup.getDetails = MagicMock(return_value={"id": 42})

        spacecmd.activationkey.do_activationkey_removegroups(shell, "key group")
        assert not shell.help_activationkey_removegroups.called
        assert shell.client.activationkey.removeServerGroups.called
        session, fun, args = shell.client.activationkey.removeServerGroups.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == [42]

    def test_do_activationkey_addentitlements_noargs(self, shell):
        """
        Test addentitlements without args calls help.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "")
        assert shell.help_activationkey_addentitlements.called
        assert not shell.client.activationkey.addEntitlements.called

    def test_do_activationkey_addentitlements_help_args(self, shell):
        """
        Test addentitlements method call shows help if only one argument is passed.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "key")
        assert shell.help_activationkey_addentitlements.called
        assert not shell.client.activationkey.addEntitlements.called

    def test_do_activationkey_addentitlements_args(self, shell):
        """
        Test "addentitlements" method calls "addEntitlements" API call.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "key entitlement")
        assert not shell.help_activationkey_addentitlements.called
        assert shell.client.activationkey.addEntitlements.called
        session, fun, args = shell.client.activationkey.addEntitlements.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == ['entitlement']

    def test_do_activationkey_addentitlements_noargs(self, shell):
        """
        Test addentitlements without args calls help.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "")
        assert shell.help_activationkey_addentitlements.called
        assert not shell.client.activationkey.addEntitlements.called

    def test_do_activationkey_addentitlements_help_args(self, shell):
        """
        Test addentitlements method call shows help if only one argument is passed.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "key")
        assert shell.help_activationkey_addentitlements.called
        assert not shell.client.activationkey.addEntitlements.called

    def test_do_activationkey_addentitlements_args(self, shell):
        """
        Test "addentitlements" method calls "addEntitlements" API call.
        """
        shell.help_activationkey_addentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_addentitlements(shell, "key entitlement")
        assert not shell.help_activationkey_addentitlements.called
        assert shell.client.activationkey.addEntitlements.called
        session, fun, args = shell.client.activationkey.addEntitlements.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == ['entitlement']

    def test_do_activationkey_removeentitlements_noargs(self, shell):
        """
        Test removeentitlements without args calls help.
        """
        shell.help_activationkey_removeentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_removeentitlements(shell, "")
        assert shell.help_activationkey_removeentitlements.called
        assert not shell.client.activationkey.removeEntitlements.called

    def test_do_activationkey_removeentitlements_help_args(self, shell):
        """
        Test removeentitlements method call shows help if only one argument is passed.
        """
        shell.help_activationkey_removeentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_removeentitlements(shell, "key")
        assert shell.help_activationkey_removeentitlements.called
        assert not shell.client.activationkey.removeEntitlements.called

    def test_do_activationkey_removeentitlements_args(self, shell):
        """
        Test "removeentitlements" method calls "removeEntitlements" API call.
        """
        shell.help_activationkey_removeentitlements = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.removeEntitlements = MagicMock()

        spacecmd.activationkey.do_activationkey_removeentitlements(shell, "key entitlement")
        assert not shell.help_activationkey_removeentitlements.called
        assert shell.client.activationkey.removeEntitlements.called
        session, fun, args = shell.client.activationkey.removeEntitlements.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == ['entitlement']

    def test_do_activationkey_addchildchannels_noargs(self, shell):
        """
        Test addchildchannels without args calls help.
        """
        shell.help_activationkey_addchildchannels = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addChildChannels = MagicMock()

        spacecmd.activationkey.do_activationkey_addchildchannels(shell, "")
        assert shell.help_activationkey_addchildchannels.called
        assert not shell.client.activationkey.addChildChannels.called

    def test_do_activationkey_addchildchannels_help_args(self, shell):
        """
        Test addchildchannels method call shows help if only one argument is passed.
        """
        shell.help_activationkey_addchildchannels = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addChildChannels = MagicMock()

        spacecmd.activationkey.do_activationkey_addchildchannels(shell, "key")
        assert shell.help_activationkey_addchildchannels.called
        assert not shell.client.activationkey.addChildChannels.called

    def test_do_activationkey_addchildchannels_args(self, shell):
        """
        Test "addchildchannels" method calls "addChildChannels" API call.
        """
        shell.help_activationkey_addchildchannels = MagicMock()
        shell.client = MagicMock()
        shell.client.activationkey = MagicMock()
        shell.client.activationkey.addChildChannels = MagicMock()

        spacecmd.activationkey.do_activationkey_addchildchannels(shell, "key some_channel")
        assert not shell.help_activationkey_addchildchannels.called
        assert shell.client.activationkey.addChildChannels.called
        session, fun, args = shell.client.activationkey.addChildChannels.call_args_list[0][0]
        assert session == shell.session
        assert fun == "key"
        assert isinstance(args, list)
        assert len(args) == 1
        assert args == ['some_channel']

