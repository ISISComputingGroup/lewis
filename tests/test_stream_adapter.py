from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, AsyncMock, patch

from parameterized import parameterized

from lewis.adapters.stream import StreamHandler


class TestStreamHandler(IsolatedAsyncioTestCase):
    def setUp(self):
        self.target = MagicMock()
        self.stream_server = MagicMock()
        self.stream_reader = AsyncMock()
        self.stream_writer = MagicMock()
        self.stream_writer.drain = AsyncMock()
        self.handler = StreamHandler(
            reader=AsyncMock(),
            writer=self.stream_writer,
            target=self.target,
            stream_server=self.stream_server)

    @parameterized.expand(
        [
            (b"\n", "test", b"test\n"),
            (b"\n", b"test", b"test\n"),
            ("\n", "test", b"test\n"),
            ("\n", "test", b"test\n"),
        ]
    )
    async def test_terminator_and_replies_of_different_types_can_be_concatenated(
        self, terminator, message, expected
    ):
        self.target.out_terminator = terminator
        await self.handler.unsolicited_reply(message)

        with patch.object(
                self.stream_writer, 'write', return_value=None) as mock_write:
            self.stream_writer.write(expected)

        mock_write.assert_called_once_with(expected)

        with patch.object(
                self.stream_writer, 'drain', return_value=None) as mock_drain:
            await self.stream_writer.drain()

        mock_drain.assert_called_once()
