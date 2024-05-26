def dict_search(d,key):

    if not d or not key:
        return None
    elif isinstance(d, dict):
        if key in d:
            return d.get(key)
        else:
            l = [dict_search(d.get(dkey),key) for dkey in d if isinstance(d.get(dkey),dict) or isinstance(d.get(dkey),list)]
            return [lv for lv in l if not lv is None].pop(0) if any(l) else None
    elif isinstance(d,list):
        li = [dict_search(e,key) for e in d if isinstance(e,dict) or isinstance(e,list)]
        return [liv for liv in li if not liv is None].pop(0) if any(li) else None
    else:
        return None
