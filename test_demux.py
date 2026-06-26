import unittest
from queue import SimpleQueue
import sys
import types

fake_fast_core = types.ModuleType("PyCriUsm.fast_core")
fake_fast_core.UsmCrypter = object
fake_fast_core.HcaCrypter = object
fake_fast_core.FastUsmFile = object
sys.modules.setdefault("PyCriUsm.fast_core", fake_fast_core)

from PyCriUsm.demux import iter_ordered_chunks


class FakeChunk(bytes):
    def __new__(cls, payload: bytes, index: int, is_video: bool, chno: int):
        obj = super().__new__(cls, payload)
        obj.index = index
        obj.is_video = is_video
        obj.chno = chno
        obj.size = len(payload)
        return obj


class DemuxOrderingTest(unittest.TestCase):
    def test_iter_ordered_chunks_reorders_without_cross_stream_mixups(self):
        queue = SimpleQueue()
        queue.put(FakeChunk(b"video-0", 0, True, 0))
        queue.put(FakeChunk(b"video-2", 2, True, 0))
        queue.put(FakeChunk(b"audio-1", 1, False, 0))
        queue.put(3)

        ordered = list(iter_ordered_chunks(queue))

        self.assertEqual([chunk.index for chunk in ordered], [0, 1, 2])
        self.assertEqual(
            [bytes(chunk) for chunk in ordered],
            [b"video-0", b"audio-1", b"video-2"],
        )


if __name__ == "__main__":
    unittest.main()
