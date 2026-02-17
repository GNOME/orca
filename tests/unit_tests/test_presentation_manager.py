# Unit tests for presentation_manager.py methods.
#
# Copyright 2026 Igalia, S.L.
# Author: Joanmarie Diggs <jdiggs@igalia.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., Franklin Street, Fifth Floor,
# Boston MA  02110-1301 USA.

# pylint: disable=wrong-import-position
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods
# pylint: disable=too-many-statements

"""Unit tests for presentation_manager.py methods."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from .orca_test_context import OrcaTestContext


@pytest.mark.unit
class TestPresentationManager:
    """Test PresentationManager class methods."""

    def _setup_dependencies(self, test_context: OrcaTestContext) -> dict[str, MagicMock]:
        """Returns dependencies for presentation_manager module testing."""

        additional_modules = [
            "orca.braille_presenter",
            "orca.live_region_presenter",
            "orca.sound_presenter",
            "orca.speech_manager",
            "orca.speech_presenter",
            "orca.typing_echo_presenter",
        ]
        essential_modules = test_context.setup_shared_dependencies(additional_modules)

        debug_mock = essential_modules["orca.debug"]
        debug_mock.print_message = test_context.Mock()
        debug_mock.print_tokens = test_context.Mock()
        debug_mock.print_exception = test_context.Mock()
        debug_mock.debugFile = None
        debug_mock.LEVEL_INFO = 800
        debug_mock.LEVEL_WARNING = 600

        braille_mock = essential_modules["orca.braille"]
        braille_mock.killFlash = test_context.Mock()
        braille_mock.displayMessage = test_context.Mock()
        braille_mock.clear = test_context.Mock()
        mock_line = test_context.Mock()
        mock_line.regions = []
        mock_line.add_regions = test_context.Mock(side_effect=mock_line.regions.append)
        braille_mock.Line = test_context.Mock(return_value=mock_line)
        braille_mock.add_line = test_context.Mock()
        braille_mock.setFocus = test_context.Mock()
        braille_mock.refresh = test_context.Mock()

        braille_presenter_mock = essential_modules["orca.braille_presenter"]
        braille_presenter_instance = test_context.Mock()
        braille_presenter_instance.use_braille = test_context.Mock(return_value=True)
        braille_presenter_instance.get_flash_messages_are_enabled = test_context.Mock(
            return_value=True
        )
        braille_presenter_instance.get_flash_messages_are_detailed = test_context.Mock(
            return_value=True
        )
        braille_presenter_instance.get_flashtime_from_settings = test_context.Mock(
            return_value=5000
        )
        braille_presenter_instance.kill_flash = test_context.Mock()
        braille_presenter_instance.present_message = test_context.Mock()
        braille_presenter_instance.present_regions = test_context.Mock()
        braille_presenter_mock.get_presenter = test_context.Mock(
            return_value=braille_presenter_instance
        )

        live_region_presenter_mock = essential_modules["orca.live_region_presenter"]
        live_region_instance = test_context.Mock()
        live_region_instance.flush_messages = test_context.Mock()
        live_region_presenter_mock.get_presenter = test_context.Mock(
            return_value=live_region_instance
        )

        sound_presenter_mock = essential_modules["orca.sound_presenter"]
        sound_presenter_instance = test_context.Mock()
        sound_presenter_instance.play = test_context.Mock()
        sound_presenter_mock.get_presenter = test_context.Mock(
            return_value=sound_presenter_instance
        )

        speech_manager_mock = essential_modules["orca.speech_manager"]
        speech_manager_instance = test_context.Mock()
        speech_manager_instance.interrupt_speech = test_context.Mock()
        speech_manager_instance.start_speech = test_context.Mock()
        speech_manager_instance.shutdown_speech = test_context.Mock()
        speech_manager_instance.refresh_speech = test_context.Mock()
        speech_manager_mock.get_manager = test_context.Mock(return_value=speech_manager_instance)

        speech_presenter_mock = essential_modules["orca.speech_presenter"]
        speech_presenter_instance = test_context.Mock()
        speech_presenter_instance.present_key_event = test_context.Mock()
        speech_presenter_instance.present_message = test_context.Mock()
        speech_presenter_instance.speak_message = test_context.Mock()
        speech_presenter_instance.speak_contents = test_context.Mock()
        speech_presenter_instance.speak_character = test_context.Mock()
        speech_presenter_instance.spell_item = test_context.Mock()
        speech_presenter_instance.spell_phonetically = test_context.Mock()
        speech_presenter_mock.get_presenter = test_context.Mock(
            return_value=speech_presenter_instance
        )

        typing_echo_presenter_mock = essential_modules["orca.typing_echo_presenter"]
        typing_echo_instance = test_context.Mock()
        typing_echo_instance.echo_keyboard_event = test_context.Mock()
        typing_echo_presenter_mock.get_presenter = test_context.Mock(
            return_value=typing_echo_instance
        )

        script_manager_mock = essential_modules["orca.script_manager"]
        mock_script = test_context.Mock()
        mock_script.speech_generator.voice = test_context.Mock(return_value=[{"family": "default"}])
        mock_script.speech_generator.generate_contents = test_context.Mock(
            return_value=["generated speech"]
        )
        mock_script.braille_generator.generate_contents = test_context.Mock(
            return_value=([test_context.Mock()], test_context.Mock())
        )
        script_manager_instance = test_context.Mock()
        script_manager_instance.get_active_script = test_context.Mock(return_value=mock_script)
        script_manager_mock.get_manager = test_context.Mock(return_value=script_manager_instance)

        return essential_modules

    def test_get_manager_returns_singleton(self, test_context: OrcaTestContext) -> None:
        """Test get_manager returns the same instance."""

        self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager1 = get_manager()
        manager2 = get_manager()

        assert manager1 is manager2
        assert manager1.__class__.__name__ == "PresentationManager"

    def test_interrupt_presentation(self, test_context: OrcaTestContext) -> None:
        """Test interrupt_presentation interrupts speech and braille."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.interrupt_presentation()

        speech_manager = essential_modules["orca.speech_manager"].get_manager()
        speech_manager.interrupt_speech.assert_called_once()
        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.kill_flash.assert_called_once()
        live_region = essential_modules["orca.live_region_presenter"].get_presenter()
        live_region.flush_messages.assert_called_once()

    def test_interrupt_presentation_without_kill_flash(self, test_context: OrcaTestContext) -> None:
        """Test interrupt_presentation with kill_flash=False."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.interrupt_presentation(kill_flash=False)

        speech_manager = essential_modules["orca.speech_manager"].get_manager()
        speech_manager.interrupt_speech.assert_called_once()
        essential_modules["orca.braille"].killFlash.assert_not_called()

    def test_present_keyboard_event(self, test_context: OrcaTestContext) -> None:
        """Test present_keyboard_event delegates to typing_echo_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_script = test_context.Mock()
        mock_event = test_context.Mock()

        manager.present_keyboard_event(mock_script, mock_event)

        typing_echo = essential_modules["orca.typing_echo_presenter"].get_presenter()
        typing_echo.echo_keyboard_event.assert_called_once_with(mock_script, mock_event)

    def test_present_key_event_delegates(self, test_context: OrcaTestContext) -> None:
        """Test present_key_event delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_event = test_context.Mock()
        manager.present_key_event(mock_event)

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.present_key_event.assert_called_once_with(mock_event)

    def test_present_message_delegates_speech(self, test_context: OrcaTestContext) -> None:
        """Test present_message delegates speech to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.present_message("This is a full message")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.present_message.assert_called_once_with(
            "This is a full message",
            "This is a full message",
            voice=None,
            reset_styles=True,
            obj=None,
        )
        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.present_message.assert_called()

    def test_present_message_with_brief(self, test_context: OrcaTestContext) -> None:
        """Test present_message with both full and brief messages."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.present_message("Full message", brief="Brief")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.present_message.assert_called_once_with(
            "Full message", "Brief", voice=None, reset_styles=True, obj=None
        )

    def test_present_message_empty_string(self, test_context: OrcaTestContext) -> None:
        """Test present_message with empty string returns early."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.present_message("")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.present_message.assert_not_called()
        essential_modules["orca.braille"].displayMessage.assert_not_called()

    def test_present_message_braille_disabled(self, test_context: OrcaTestContext) -> None:
        """Test present_message when braille is disabled."""

        essential_modules = self._setup_dependencies(test_context)
        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.use_braille.return_value = False

        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.present_message("Test message")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.present_message.assert_called()
        essential_modules["orca.braille"].displayMessage.assert_not_called()

    def test_play_sound(self, test_context: OrcaTestContext) -> None:
        """Test play_sound delegates to sound_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import PresentationManager

        mock_sound = test_context.Mock()
        PresentationManager.play_sound(mock_sound)

        sound_presenter = essential_modules["orca.sound_presenter"].get_presenter()
        sound_presenter.play.assert_called_once_with(mock_sound, True)

    def test_play_sound_no_interrupt(self, test_context: OrcaTestContext) -> None:
        """Test play_sound with interrupt=False."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import PresentationManager

        mock_sound = test_context.Mock()
        PresentationManager.play_sound(mock_sound, interrupt=False)

        sound_presenter = essential_modules["orca.sound_presenter"].get_presenter()
        sound_presenter.play.assert_called_once_with(mock_sound, False)

    def test_present_braille_message(self, test_context: OrcaTestContext) -> None:
        """Test present_braille_message shows braille message."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import PresentationManager

        PresentationManager.present_braille_message("Test braille", restore_previous=False)

        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.present_message.assert_called_once_with(
            "Test braille", restore_previous=False
        )

    def test_present_braille_message_braille_disabled(self, test_context: OrcaTestContext) -> None:
        """Test present_braille_message delegates even when braille is disabled."""

        essential_modules = self._setup_dependencies(test_context)
        braille_presenter_instance = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter_instance.use_braille.return_value = False

        from orca.presentation_manager import PresentationManager

        PresentationManager.present_braille_message("Test braille")

        braille_presenter_instance.present_message.assert_called_once()

    def test_spell_item_delegates(self, test_context: OrcaTestContext) -> None:
        """Test spell_item delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.spell_item("abc")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.spell_item.assert_called_once_with("abc")

    def test_spell_phonetically_delegates(self, test_context: OrcaTestContext) -> None:
        """Test spell_phonetically delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.spell_phonetically("ab")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.spell_phonetically.assert_called_once_with("ab")

    def test_speak_character_delegates(self, test_context: OrcaTestContext) -> None:
        """Test speak_character delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.speak_character("a")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.speak_character.assert_called_once_with("a")

    def test_speak_message_delegates(self, test_context: OrcaTestContext) -> None:
        """Test speak_message delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.speak_message("Hello world")

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.speak_message.assert_called_once_with(
            "Hello world", voice=None, reset_styles=True, obj=None
        )

    def test_speak_message_with_args_delegates(self, test_context: OrcaTestContext) -> None:
        """Test speak_message passes all arguments to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_voice = test_context.Mock()
        mock_obj = test_context.Mock()
        manager.speak_message(
            "Hello world",
            voice=mock_voice,
            reset_styles=False,
            obj=mock_obj,
        )

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.speak_message.assert_called_once_with(
            "Hello world",
            voice=mock_voice,
            reset_styles=False,
            obj=mock_obj,
        )

    def test_speak_contents_delegates(self, test_context: OrcaTestContext) -> None:
        """Test speak_contents delegates to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        manager.speak_contents(mock_contents)

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.speak_contents.assert_called_once_with(mock_contents)

    def test_speak_contents_with_kwargs_delegates(self, test_context: OrcaTestContext) -> None:
        """Test speak_contents passes keyword arguments to speech_presenter."""

        essential_modules = self._setup_dependencies(test_context)
        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        mock_prior = test_context.Mock()
        manager.speak_contents(mock_contents, priorObj=mock_prior)

        speech_pres = essential_modules["orca.speech_presenter"].get_presenter()
        speech_pres.speak_contents.assert_called_once_with(mock_contents, priorObj=mock_prior)

    def test_display_contents(self, test_context: OrcaTestContext) -> None:
        """Test display_contents generates and displays braille."""

        essential_modules = self._setup_dependencies(test_context)

        # Set up a proper regions list structure (list of lists of regions)
        mock_region = test_context.Mock()
        mock_region.string = "test "
        script_manager = essential_modules["orca.script_manager"].get_manager()
        script = script_manager.get_active_script()
        script.braille_generator.generate_contents.return_value = ([[mock_region]], mock_region)

        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        manager.display_contents(mock_contents)

        script.braille_generator.generate_contents.assert_called_once()
        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.present_regions.assert_called()

    def test_display_contents_braille_disabled(self, test_context: OrcaTestContext) -> None:
        """Test display_contents returns early when braille is disabled."""

        essential_modules = self._setup_dependencies(test_context)
        braille_presenter_instance = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter_instance.use_braille.return_value = False

        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        manager.display_contents(mock_contents)

        braille_presenter_instance.present_regions.assert_not_called()

    def test_display_contents_no_active_script(self, test_context: OrcaTestContext) -> None:
        """Test display_contents returns early when no active script."""

        essential_modules = self._setup_dependencies(test_context)
        script_manager = essential_modules["orca.script_manager"].get_manager()
        script_manager.get_active_script.return_value = None

        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        manager.display_contents(mock_contents)

        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.present_regions.assert_not_called()

    def test_display_contents_empty_regions(self, test_context: OrcaTestContext) -> None:
        """Test display_contents handles empty regions list."""

        essential_modules = self._setup_dependencies(test_context)
        script_manager = essential_modules["orca.script_manager"].get_manager()
        script = script_manager.get_active_script()
        script.braille_generator.generate_contents.return_value = ([], None)

        from orca.presentation_manager import get_manager

        manager = get_manager()
        mock_contents = [(test_context.Mock(), 0, 10, "test text")]
        manager.display_contents(mock_contents)

        braille_presenter = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter.present_regions.assert_not_called()

    @pytest.mark.parametrize(
        "flash_enabled,use_braille,expected_flash_called",
        [
            pytest.param(True, True, True, id="flash_and_braille_enabled"),
            pytest.param(False, True, False, id="flash_disabled"),
            pytest.param(True, False, False, id="braille_disabled"),
            pytest.param(False, False, False, id="both_disabled"),
        ],
    )
    def test_present_message_braille_conditions(
        self,
        test_context: OrcaTestContext,
        flash_enabled: bool,
        use_braille: bool,
        expected_flash_called: bool,
    ) -> None:
        """Test present_message braille behavior under various conditions."""

        essential_modules = self._setup_dependencies(test_context)
        braille_presenter_instance = essential_modules["orca.braille_presenter"].get_presenter()
        braille_presenter_instance.use_braille.return_value = use_braille
        braille_presenter_instance.get_flash_messages_are_enabled.return_value = flash_enabled

        from orca.presentation_manager import get_manager

        manager = get_manager()
        manager.present_message("Test message")

        if expected_flash_called:
            braille_presenter_instance.present_message.assert_called()
        else:
            braille_presenter_instance.present_message.assert_not_called()
