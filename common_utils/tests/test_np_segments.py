import hypothesis as hyp
import hypothesis.strategies as hyp_st
import hypothesis.extra.numpy as hyp_np
import numpy as np

from nre_utils import np_segments


@hyp_st.composite
def unique_elem_array_and_axis(draw):
    shape = draw(hyp_np.array_shapes(min_dims=1))
    dtype = draw(hyp_np.integer_dtypes() | hyp_np.floating_dtypes())

    array = np.arange(np.prod(shape), dtype=dtype).reshape(shape)
    axis = draw(hyp_st.integers(-array.ndim, array.ndim - 1))
    return array, axis


@hyp.given(
    array_axis=unique_elem_array_and_axis(),
    nperseg=hyp_st.integers(1, np.iinfo(np.int64).max),
    step=hyp_st.integers(1, np.iinfo(np.int64).max),
)
def test_np_segments(array_axis, nperseg, step):
    array, axis = array_axis

    calc_view, calc_excess = np_segments.segment_view(array, nperseg, step, axis)

    axis = axis % array.ndim

    i = -1
    for i in range(0, calc_view.shape[axis]):
        assert np.all(
            calc_view.take(i, axis)
            == array.take(np.arange(i * step, i * step + nperseg), axis)
        )
    assert np.all(
        calc_excess == array.take(np.arange((i + 1) * step, array.shape[axis]), axis)
    )

    assert np.may_share_memory(calc_view, array) or calc_view.size == 0
    assert np.may_share_memory(calc_excess, array) or calc_excess.size == 0
