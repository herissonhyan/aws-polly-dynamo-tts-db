import hashlib


def generate_short_id(phrase):
    # Codificar a frase em bytes
    phrase_bytes = phrase.encode()

    # Gerar o hash sha256 da frase
    sha256 = hashlib.sha256(phrase_bytes)

    # Converter o hash em uma representação binária
    bin_sha256 = sha256.digest()

    # Selecionar os primeiros n dígitos
    short_id = bin_sha256[:8]

    # Converter a representação binária de volta para hexadecimal
    hex_short_id = short_id.hex()

    return hex_short_id
