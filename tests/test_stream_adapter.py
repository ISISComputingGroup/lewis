import asyncio
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock

from parameterized import parameterized

from lewis.adapters.stream import StreamHandler


class TestStreamHandler(IsolatedAsyncioTestCase):
    def setUp(self):
        self.target = MagicMock()
        self.stream_server = MagicMock()
        self.stream_reader = AsyncMock()
        self.stream_writer = MagicMock()
        self.stream_writer.drain = AsyncMock()
        self.stream_writer.wait_closed = AsyncMock()
        self.stream_writer.is_closing.return_value = False
        self.handler = StreamHandler(
            reader=self.stream_reader,
            writer=self.stream_writer,
            target=self.target,
            stream_server=self.stream_server)
        self.handler._readtimeout = 0
        self.handler._in_terminator = b"\r\n"
        self.target.out_terminator = "\r\n"

    def _create_mock_command(self, can_process=lambda x: True, response="OK"):
        cmd_mock = MagicMock()
        cmd_mock.can_process.side_effect = can_process
        cmd_mock.process_request.return_value = response
        return cmd_mock

    @parameterized.expand(
        [
            (b"\n", "test", b"test\n"),
            (b"\n", b"test", b"test\n"),
            ("\n", "test", b"test\n"),
            ("\r\n", "test", b"test\r\n"),
        ]
    )
    async def test_terminator_and_replies_of_different_types_can_be_concatenated(
        self, terminator, message, expected
    ):
        self.target.out_terminator = terminator
        # unsolicited_reply is sync and uses run_coroutine_threadsafe; it must be called
        # from a worker thread so that .result() does not block the running event loop.
        self.stream_server._loop = asyncio.get_running_loop()
        await asyncio.get_running_loop().run_in_executor(
            None, self.handler.unsolicited_reply, message
        )

        self.stream_writer.write.assert_called_once_with(expected)

    async def test_process_starts_pending_read_on_first_call(self):
        await self.handler.process(10)

        self.assertIsNotNone(self.handler._pending_read)

    async def test_process_eof_triggers_handle_close(self):
        self.handler._reader.read.return_value = b""

        await self.handler.process(10)
        await asyncio.sleep(0)
        await self.handler.process(10)

        self.stream_server.remove_handler.assert_called_with(self.handler)

    async def test_process_dispatches_single_command_with_terminator(self):
        cmd_mock = self._create_mock_command()
        self.target.bound_commands = [cmd_mock]
        self.handler._reader.read.return_value = b"CMD\r\n"

        await self.handler.process(10)
        await asyncio.sleep(0)
        await self.handler.process(10)

        cmd_mock.can_process.assert_called_with(b"CMD")
        cmd_mock.process_request.assert_called_with(b"CMD")

        self.stream_writer.write.assert_called_once_with(b"OK\r\n")

    async def test_process_dispatches_two_commands_in_one_chunk(self):
        cmd1_mock = self._create_mock_command(
            can_process=lambda x: x == b"CMD1",
            response="OK1")
        cmd2_mock = self._create_mock_command(
            can_process=lambda x: x == b"CMD2",
            response="OK2")
        self.target.bound_commands = [cmd1_mock, cmd2_mock]
        self.handler._reader.read.return_value = b"CMD1\r\nCMD2\r\n"

        await self.handler.process(10)
        await asyncio.sleep(0)
        await self.handler.process(10)

        cmd1_mock.can_process.assert_called()
        cmd2_mock.can_process.assert_called()
        cmd1_mock.process_request.assert_called_once_with(b"CMD1")
        cmd2_mock.process_request.assert_called_once_with(b"CMD2")

        self.stream_writer.write.assert_any_call(b"OK1\r\n")
        self.stream_writer.write.assert_any_call(b"OK2\r\n")
        self.assertEqual(self.stream_writer.write.call_count, 2)

    async def test_process_timeout_with_incomplete_command_sends_error(self):
        self.handler._readtimeout = 10
        self.handler._reader.read.return_value = b"INCOMPLETE"

        # First call: starts the read task
        await self.handler.process(10)
        await asyncio.sleep(0)
        # Second call: collects data; _readtimer resets to 0, then increments to 10
        await self.handler.process(10)
        # Third call: _readtimer (10) >= _readtimeout (10) -> timeout fires, error reply sent
        await self.handler.process(10)

        self.target.handle_error.assert_called_once()
        self.stream_writer.write.assert_called_once()
