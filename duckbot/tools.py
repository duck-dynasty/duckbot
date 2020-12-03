def make_correction(author, message):
    kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
    for k in kubes:
        if k in message:
            return "I think {0} means K8s".format(author)
    
    if "bitcoin" in message:
        return "Magic Beans*"

    return None
# end def make_correction
