from lxml import etree
from pprint import pprint
from bs4 import BeautifulSoup
import re
#import helpers
#import sqlalchemy


def main():
	base_path = "/Users/asilva/CAP_Working_Data/twovolz/"
	barcode = "32044026226753"
	case_no = 7
	version  = "redacted"
	case_map(base_path, barcode, case_no, version)


def case_map(base_path, barcode, case_no, version):
	
	volume_path = "{}{}_{}/".format(base_path, barcode, version)
	case_path = "{}/casemets/{}_{}_CASEMETS_{}.xml".format(volume_path, barcode, version, format(case_no, '04'))

	case_soup = BeautifulSoup( open(case_path), "xml")

	alto_files = _get_alto_files(case_soup, volume_path)

	blocks = case_soup.find_all(TYPE="blocks")
	case_soup = case_soup.find(USE="casebody")
	case_id = case_soup.file['ID']
	casebody = case_soup.file.FContent.xmlData.casebody

	#<docketnumber pgmap="40" id="b40-9">No. 131</docketnumber>
	#<docketnumber pgmap="41" id="A32">Number: 26068.</docketnumber>
	#<parties pgmap="40" id="b40-10">LEONARD F. PARKER v. RAYMEN A. MORRELL</parties>
	#<decisiondate pgmap="40" id="Ae">Decided: Sept. 22, 1976</decisiondate>
	#<otherdate pgmap="40" id="b40-13">Argued: March 17, 1976.</otherdate>

	#<p pgmap="40" id="pAza">Southern District</p>
	#<p pgmap="41" id="b41-8">Case tried to Sullivan, J., in the District Court of Southern Norfolk.</p>
	#<p pgmap="41" id="b41-9">Justices: Lee, P.J., Rider, Welsh, J.J.</p>




def _get_alto_files(case_soup, volume_path):
	'''

		{'alto_00020_1': {'path': '../alto/32044026226753_redacted_ALTO_00020_1.xml', 'pgmap': '40'},
		 'alto_00021_0': {'path': '../alto/32044026226753_redacted_ALTO_00021_0.xml', 'pgmap': '41'}}
	'''

	alto_map = {}
	page_map = case_soup.find(TYPE="physical").div

	# this loop grabs the page numbers from the <structMap TYPE="physical"> section 
	for page in page_map:
		if page.name is None:
			continue
		alto_id = page.find("fptr", FILEID=re.compile("alto_"))['FILEID']
		if alto_id not in alto_map:
			alto_map[alto_id] = {}
		alto_map[alto_id]['pgmap'] = page['ORDER']

	# this loop grabs the relative paths from the <fileGrp USE="alto> section
	alto_files = case_soup.find(USE="alto")
	for alto in alto_files:
		if alto.name is None:
			continue
		alto_id = alto['ID']
		path = alto.FLocat['xlink:href']
		alto_map[alto_id]['path'] = path
		alto_map[alto_id]['contents'] = _map_alto_file(path.replace("../", volume_path))

	return alto_map


def _map_alto_file(alto_path):
	#TODO get the map words/lines/blocks/elements of the alto files 
	alto_soup = BeautifulSoup( open(alto_path), "xml")

	for text_block in alto_soup.find("PrintSpace"):
		print(text_block.name)
	return []

def _get_case_string_fs():

	pass

def _get_case_string_s3():
	#TODO
	pass

if __name__ == '__main__':
	main()
