class CaseXML(object):
  """Use this class for updating cases
  Arguments:
  barcode(str) -- barcode of the volume
  case_no(int) -- case number 

  """
  def __init__(self, barcode, case_no):
    super(CaseXML, self).__init__()


    self.barcode = barcode
    self.case_no = case_no


    # this is just test data to populate teh case_file and alto_file stuff. 
    # maybe these alto files shouldn't be eager loaded... maybe a lazy getter?
    base_path = "/Users/asilva/CAP_Working_Data/twovolz/"
    version  = "redacted"
    volume_path = "{}{}_{}/".format(base_path, barcode, version)
    case_path = "{}casemets/{}_{}_CASEMETS_{}.xml".format(volume_path, barcode, version, format(case_no, '04'))

    alto_ids = [ "alto_00021_0", "alto_00021_1", "alto_00022_0", "alto_00022_1", "alto_00023_0", "alto_00023_1", "alto_00024_0" ]

    self.alto_files = { alto_id : open("{}alto/{}_{}_{}.xml".format(volume_path, barcode, version, alto_id.upper())) for alto_id in alto_ids }
    self.case_xml = open(case_path)




  def casebody_tag_name_by_id(self, casemets_id, new_name):
    """Change a tag name by element ID. Will modify it in ALTO if present.

    Arguments:
    element_id(str) -- the id attribute of the tag you're changin 
    tag_name(str) -- the new tag name

    Returns: 
    {True, 'Successful (etc)'} -- if successful
    {False, '(reason)'} -- if unsuccessful
    """
    from bs4 import BeautifulSoup
    #the IDs differ from ALTO to CASEMETS... generate the ALTO specific one
    alto_id = casemets_id.replace('-', '.').replace('b', 'BL_')
    case_soup = BeautifulSoup( self.case_xml, "xml")
    elements = case_soup.find_all(id=casemets_id)
    if len(elements) > 1:
      return {False, 'Ambiguous ID. Returned multiple tags.'}
    elif len(elements) == 0:
      return {False, 'Element not found.'}

    #change the name in the casemets
    old_name = elements[0].name
    elements[0].name = new_name
    

    #find out which alto file it's in, and update that
    alto_file = case_soup.find(BEGIN=alto_id)['FILEID']
    alto_soup = BeautifulSoup( self.alto_files[alto_file], "xml")
    alto_element = alto_soup.find(ID=casemets_id)
    alto_element['LABEL'] = new_name

    return {True, "Successful. Tag {} with id {} successfully changed to {}. Database record will not be updated until update() is called."} 


  def tag_name_by_contents():
    #TODO
    pass

  def tag_contents_by_id():
    #TODO
    pass

  def attribute_name_by_id():
    #TODO
    pass

  def attribute_contents_by_id():
    #TODO
    pass

