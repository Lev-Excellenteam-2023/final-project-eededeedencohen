import pytest
from Explainer.Parser.parse_pptx_file import get_list_of_content_from_pptx_file, get_list_of_content_from_pptx_bytes
from DB.schema import get_pptx_bytes


@pytest.mark.asyncio
async def test_compare_parse_functions_output():
    file_path = "../../files/asyncio-intro.pptx"
    pptx_bytes = get_pptx_bytes(1)

    content_from_file = await get_list_of_content_from_pptx_file(file_path)
    content_from_bytes = await get_list_of_content_from_pptx_bytes(pptx_bytes)

    # Assert that the outputs are identical
    assert content_from_file == content_from_bytes


