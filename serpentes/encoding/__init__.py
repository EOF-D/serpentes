from __future__ import annotations

import typing
from codecs import BufferedIncrementalDecoder, CodecInfo, register, utf_8_encode
from traceback import format_exc


class _IncrDecoder(BufferedIncrementalDecoder):
    def _buffer_decode(self, data: bytes, *_: tuple[str, bool]) -> tuple[str, int]:
        if data != b"":
            return decode(data)

        return str(), 0


def decode(input: bytes | memoryview, errors: str = "strict") -> tuple[str, int]:
    parse: bytes = typing.cast(bytes, input)

    if isinstance(input, memoryview):
        parse = input.tobytes()

    try:
        return parse.decode(), len(parse)
    except Exception:
        print(format_exc)
        print(errors)
        raise


ENCODINGS: dict[str, CodecInfo] = {
    encoding: CodecInfo(
        decode=decode,
        encode=utf_8_encode,  # pyright: ignore
        name=encoding,
        incrementaldecoder=_IncrDecoder,
    )
    for encoding in {"Serpentes", "serpentes"}
}


register(ENCODINGS.get)
