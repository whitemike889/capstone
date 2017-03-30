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
		block = case_soup.find(id=alto_id)
		path = alto.FLocat['xlink:href']
		alto_map[alto_id]['path'] = path

		#gets a map of the contents of the file
		alto_map[alto_id]['contents'] = _map_alto_file(path.replace("../", volume_path), case_soup)

	return alto_map

#TODO: clean up this pile of hot garbage masquerading as properly passing arguments
def _map_alto_file(alto_path, case_soup):
	'''
		This will take an alto file, and send back a dictionary of words 
		with alto properties, organized into text blocks.
		The structure of the content in the ALTO documents is TextBlocks, 
		which contain TextLines, which contain Strings (and spaces, which 
		i treat as strings)
	'''

	alto_soup = BeautifulSoup( open(alto_path), "xml")
	alto_contents = {}

	last_id = ""
	for text_block in alto_soup.find("PrintSpace"):
		print("")
		
		if text_block.name is None:
			continue

		# block_id is the id of the block in the case mets, which is in the TAGREFS attribute of the alto text block
		block_id = text_block['TAGREFS']
		if last_id != block_id:
			enumerator = 0
			last_id = block_id
		# case_block gets the relevant block of text from the case body in the case mets file
		case_block = None
		case_mets_block = case_soup.find(id=block_id)
		if case_mets_block is not None:
			case_block = _process_case_block(case_mets_block)

		# structure_tag is a descriptor in the ALTO file saying what kind of text block it is, such as paragraph or page marker
		structure_tag = alto_soup.find(ID=block_id)

		if block_id not in alto_contents:
			 alto_contents[block_id] = []

		#then loop through the text lines
		for text_line in text_block:
			if text_line.name is None:
				continue

			#then loop through strings and spaces
			for index, string in enumerate(text_line):
				if string.name is None:
					continue
				string_map = _process_string(text_block, text_line, string)
				alto_contents[block_id].append(string_map)		
				if string_map['type'] == 'space':
					continue
				if case_block is None:
					continue

				if enumerator < len(case_block['case_words']):
					if string_map['CONTENT'] != case_block['case_words'][enumerator]:
						print("Alto: {}\t\tCasemets: {}\t\tEnum: {}".format(string_map['CONTENT'], case_block['case_words'][enumerator], enumerator))
				enumerator += 1


	return alto_contents

def _process_case_block(case_block):
	split_block_test = re.compile('[0-9]+\(([0-9]+)\)\s[0-9]+\(([0-9]+)\)')
	
	return_dict = {}

	return_dict['case_text'] = case_block.text
	return_dict['case_words'] = re.split('\s+', case_block.text)
	match = split_block_test.search(case_block['pgmap'])
	if match is not None:
		return_dict['split_block'] = True
		return_dict['split_start'] = int(match.group(1))
		return_dict['split_end'] = int(match.group(2))
	else:
		return_dict['split_block'] = False

	return return_dict


def _process_string(text_block, text_line, string):
	
	return_dict = {}
	# at this point, I'm just taking everything in SP and String tags. Not sure if I'll need it all
	# at the very least, we're going to need the letter location/geometry to split mistakenly 
	# concatenated strings. I'm sure there's a more efficient way to copy all of these properties
	# into the map, but this works well enough for now
	return_dict['text_block'] = text_block['ID']
	return_dict['text_line'] = text_line['ID']
	return_dict['id'] = string['ID']
	return_dict['HPOS'] = string['HPOS']
	return_dict['VPOS'] = string['VPOS']
	return_dict['WIDTH'] = string['WIDTH']

	if string.name == 'String':
		return_dict['type'] = 'string'
		return_dict['CONTENT'] = string['CONTENT']
		return_dict['HEIGHT'] = string['HEIGHT']
		return_dict['STYLEREFS'] = string['STYLEREFS']
		return_dict['WC'] = string['WC']
		return_dict['CC'] = string['CC']
		return_dict['TAGREFS'] = string['TAGREFS']
	elif string.name == 'SP':
		return_dict['type'] = 'space'
	else:
		raise("encountered a weird string/space tag {} in {}".format(string.name, alto_path))

	return return_dict



def _alternate_map_alto_file(alto_path):
	'''
		This will take an alto file, and send back a dictionary like this:
        'b47-6': {'BL_47.6': {'TL_47.6.1': {'SP_47.6.1.10': {'HPOS': '958', 'VPOS': '2314', 'WIDTH': '16', 'type': 'space'},
                 'ST_47.6.1.1': {'CC': '00000', 'CONTENT': 'There', 'HEIGHT': '33', 'HPOS': '342', 'STYLEREFS': 'Style_3', 'TAGREFS': '', 'VPOS': '2311', 'WC': '0.58', 'WIDTH': '109', 'type': 'string'},
		the first element is the element referenced in the CASEMETS file so it should be easy to narrow down to the text block

	'''
	alto_soup = BeautifulSoup( open(alto_path), "xml")

	alto_contents = {}

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


	return alto_contents


def _get_case_string_fs():

	pass

def _get_case_string_s3():
	#TODO
	pass

if __name__ == '__main__':
	main()
