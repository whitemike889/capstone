import re
import pytest
from scripts.helpers import parse_xml
from scripts.generate_case_html import generate_html, tag_map
from capdb.models import CaseXML

@pytest.mark.django_db
def test_generate_html_tags(ingest_case_xml):
    for case in CaseXML.objects.all():
        parsed_case_xml = parse_xml(case.orig_xml)

        # shouldn't attempt to parse a duplicative case
        if parsed_case_xml('duplicative|casebody'):
            assert generate_html(case).startswith("<h1 class='error'>")
            continue
        casebody_tree = parsed_case_xml("casebody|casebody")[0]
        casebody_html = generate_html(case).replace('\n', '').replace('\r', '').replace('\t', ' ')

        for element in casebody_tree.iter():
            old_tag = element.tag.split("}")[1]
            new_tag = 'p' if old_tag == 'p' else tag_map[old_tag]

            if 'id' in element.attrib:
                id_search = r'<' + re.escape(new_tag) + r'[^>]*id="' + re.escape(element.attrib['id'])
                assert re.search(id_search, casebody_html, re.IGNORECASE) is not None
            else:
                class_search = r'<' + re.escape(new_tag) + r'[^>]*class="' + re.escape(old_tag)
                assert re.search(class_search, casebody_html, re.IGNORECASE) is not None

@pytest.mark.django_db
def test_generate_html_footnotes(ingest_case_xml):
    for case in CaseXML.objects.all():
        parsed_case_xml = parse_xml(case.orig_xml)

        # shouldn't attempt to parse a duplicative case
        if parsed_case_xml('duplicative|casebody'):
            assert generate_html(case).startswith("<h1 class='error'>")
            continue
        casebody_html = generate_html(case).replace('\n', '').replace('\r', '').replace('\t', ' ')

        for footnote in parsed_case_xml("casebody|footnote"):
            footnote_anchor = '<a id="footnote_{}" class="footnote_anchor">'.format(footnote.attrib['label'])
            footnote_element = '<a class="footnotemark" href="#footnote_{}">{}</a>'.format(footnote.attrib['label'], footnote.attrib['label'])
            assert footnote_anchor in casebody_html
            assert footnote_element in casebody_html