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
	'''
		This will take an alto file, and send back a dictionary like this:
        'b47-6': {'BL_47.6': {'TL_47.6.1': {'SP_47.6.1.10': {'HPOS': '958', 'VPOS': '2314', 'WIDTH': '16', 'type': 'space'},
                 'ST_47.6.1.1': {'CC': '00000', 'CONTENT': 'There', 'HEIGHT': '33', 'HPOS': '342', 'STYLEREFS': 'Style_3', 'TAGREFS': '', 'VPOS': '2311', 'WC': '0.58', 'WIDTH': '109', 'type': 'string'},
		the first element is the element referenced in the CASEMETS file so it should be easy to narrow down to the text block

	'''
	alto_soup = BeautifulSoup( open(alto_path), "xml")

	alto_contents = {}
	print(alto_path)

	# First loop through the text blocks
	for text_block in alto_soup.find("PrintSpace"):
		if text_block.name is None:
			continue

		if text_block['TAGREFS'] not in alto_contents:
			 alto_contents[text_block['TAGREFS']] = []


		#then loop through the text lines
		for text_line in text_block:
			if text_line.name is None:
				continue

			#then loop through strings and spaces
			for string in text_line:
				if string.name is None:
					continue
				push_dict = {}
				# at this point, I'm just taking everything in SP and String tags. Not sure if I'll need it all
				# at the very least, we're going to need the letter location/geometry to split mistakenly 
				# concatenated strings. I'm sure there's a more efficient way to copy all of these properties
				# into the map, but this works well enough for now
				push_dict['text_block'] = text_block['ID']
				push_dict['text_line'] = text_line['ID']
				push_dict['id'] = string['ID']
				push_dict['HPOS'] = string['HPOS']
				push_dict['VPOS'] = string['VPOS']
				push_dict['WIDTH'] = string['WIDTH']

				if string.name == 'String':
					push_dict['type'] = 'string'
					push_dict['CONTENT'] = string['CONTENT']
					push_dict['HEIGHT'] = string['HEIGHT']
					push_dict['STYLEREFS'] = string['STYLEREFS']
					push_dict['WC'] = string['WC']
					push_dict['CC'] = string['CC']
					push_dict['TAGREFS'] = string['TAGREFS']
				elif string.name == 'SP':
					push_dict['type'] = 'space'
				else:
					raise("encountered a weird string/space tag {} in {}".format(string.name, alto_path))
				alto_contents[text_block['TAGREFS']].append(push_dict)		


	return alto_contents


def _alternate_map_alto_file(alto_path):
	'''
		This will take an alto file, and send back a dictionary like this:
        'b47-6': {'BL_47.6': {'TL_47.6.1': {'SP_47.6.1.10': {'HPOS': '958', 'VPOS': '2314', 'WIDTH': '16', 'type': 'space'},
                 'ST_47.6.1.1': {'CC': '00000', 'CONTENT': 'There', 'HEIGHT': '33', 'HPOS': '342', 'STYLEREFS': 'Style_3', 'TAGREFS': '', 'VPOS': '2311', 'WC': '0.58', 'WIDTH': '109', 'type': 'string'},
		the first element is the element referenced in the CASEMETS file so it should be easy to narrow down to the text block

	'''
	alto_soup = BeautifulSoup( open(alto_path), "xml")

	alto_contents = {}
	print(alto_path)

	# First loop through the text blocks
	for text_block in alto_soup.find("PrintSpace"):
		if text_block.name is None:
			continue

		if text_block['TAGREFS'] not in alto_contents:
			 alto_contents[text_block['TAGREFS']] = {}

		alto_contents[text_block['TAGREFS']][text_block['ID']] = {}

		#then loop through the text lines
		for text_line in text_block:
			if text_line.name is None:
				continue
			alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']] = {}
			#then loop through strings and spaces
			for string in text_line:
				if string.name is None:
					continue
				alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']] = {}

				# at this point, I'm just taking everything in SP and String tags. Not sure if I'll need it all
				# at the very least, we're going to need the letter location/geometry to split mistakenly 
				# concatenated strings. I'm sure there's a more efficient way to copy all of these properties
				# into the map, but this works well enough for now
				if string.name == 'SP':
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['type'] = 'space'
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['HPOS'] = string['HPOS']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['VPOS'] = string['VPOS']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['WIDTH'] = string['WIDTH']
				elif string.name == 'String':
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['type'] = 'string'
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['HPOS'] = string['HPOS']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['VPOS'] = string['VPOS']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['WIDTH'] = string['WIDTH']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['CONTENT'] = string['CONTENT']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['HEIGHT'] = string['HEIGHT']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['STYLEREFS'] = string['STYLEREFS']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['WC'] = string['WC']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['CC'] = string['CC']
					alto_contents[text_block['TAGREFS']][text_block['ID']][text_line['ID']][string['ID']]['TAGREFS'] = string['TAGREFS']


	pprint(alto_contents)
	return alto_contents


def _get_case_string_fs():

	pass

def _get_case_string_s3():
	#TODO
	pass

if __name__ == '__main__':
	main()
