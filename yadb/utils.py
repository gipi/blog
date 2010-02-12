import re

def slugify(value):
    # http://www.faqs.org/rfcs/rfc1738.html
    change_not_rfc = re.compile(r"[ _'`#:?/=@%!;.,^]").sub('-', value).lower()
    delete_multiple_dashes = re.compile(r"-+").sub('-', change_not_rfc)
    delete_trailing_dash = re.compile(r"-$").sub('', delete_multiple_dashes)

    return delete_trailing_dash
