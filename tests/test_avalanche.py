from experiments.avalanche.run import bit_difference, flip_bit, measure


def test_bit_helpers():
    assert flip_bit(b"\x00", 0) == b"\x80"
    assert flip_bit(b"\x00", 7) == b"\x01"
    assert bit_difference(b"\x00", b"\xff") == 8


def test_avalanche_experiment_has_one_sample_per_input_bit():
    result = measure(b"abc")
    assert len(result.samples) == 24
    assert all(0 < value <= 256 for value in result.samples)
    assert 0.35 < result.average_ratio < 0.65

