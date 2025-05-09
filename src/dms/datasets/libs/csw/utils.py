from lxml import etree

PARSER = etree.XMLParser(resolve_entities=False)


def get_anytext(bag):
    """
    generate bag of text for free text searches
    accepts list of words, string of XML, or etree.Element
    """

    if isinstance(bag, list):  # list of words
        return " ".join([_f for _f in bag if _f]).strip()
    else:  # xml
        if isinstance(bag, bytes) or isinstance(bag, str):
            # serialize to lxml
            bag = etree.fromstring(bag, PARSER)  # noqa: S320
        # get all XML element content
        return " ".join([value.strip() for value in bag.xpath("//text()")])
