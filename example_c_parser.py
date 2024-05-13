from openai import OpenAI

from sourcetodoc.docstring import (DocstringParser, Language, ParserLibrary,
                                   Replace, ParserName)

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
parser_lib = ParserLibrary.create_default(client)
parser = DocstringParser(parser_lib)

code = """\
    /* Get value from AAF AVTPDU field.
     * @pdu: Pointer to PDU struct.
     * @field: PDU field to be retrieved.
     * @val: Pointer to variable which the retrieved value should be saved.
     *
     * Returns:
     *    0: Success.
     *    -EINVAL: If any argument is invalid.
     */
    int avtp_aaf_pdu_get(const struct avtp_stream_pdu *pdu,
    				enum avtp_aaf_field field, uint64_t *val);
"""

result = parser.parse_string(code, Replace.APPEND_TO_OLD_COMMENTS, ParserName("c_parser"))

print(result)
