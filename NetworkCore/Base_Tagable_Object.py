import numpy as np

def_dtype = np.float64

class TaggableObjectBase:

    def __init__(self, tag):
        self.tags = []
        self.clear_cache()
        self._mat_eval_dict = {}
        if tag is not None:
            self.add_tag(tag)
        self.add_tag(self.__class__.__name__)
        self._searching = False

    def has_module(self, tag):
        return self[tag, 0] is not None

    def find_objects(self, key):  # override for deeper search
        result = []
        return result

    def clear_cache(self):
        self.tag_shortcuts = {}

    def set_tag_attrs(self, tag, attr, value):
        for obj in self[tag]:
            setattr(obj, attr, value)

    def call_tag_functions(self, tag, attr, **args):  # todo: test
        for obj in self[tag]:
            getattr(obj, attr)(args)

    def get(self, key, first=True, numpy=True):
        return self[key]  # todo

    def __getitem__(self, key):
        np_array_conversion = isinstance(key, tuple) and 'np' in key

        if isinstance(key, tuple):
            k = key[0]
            index = key[1]
        else:
            k = key
            index = None

        # cache
        if key in self.tag_shortcuts and type(self.tag_shortcuts[key]) is not np.ndarray:
            if np_array_conversion:
                result = np.array(self.tag_shortcuts[key])
            else:
                result = self.tag_shortcuts[key]

            if index is not None:
                if len(result) > 0:
                    return result[index]
                else:
                    return None
            else:
                return result

        # normal search
        result = []
        if k in self.tags or (k is type and isinstance(self, k)):
            result = [self]

        result += self.find_objects(k)

        if k not in self.tag_shortcuts:
            self.tag_shortcuts[k] = result

        if index is not None:
            if len(result) > 0:
                result = result[index]
            else:
                result = None

        if np_array_conversion:
            return np.array(result)
        else:
            return result

    def add_tag(self, tag):
        for subtag in tag.split(','):
            self.tags.append(subtag)
        return self

    #def __getattr__(self, attr_name):
    #    super().__getattr__(attr_name)

    '''
    def __getattr__(self, attr_name):
        print(attr_name)#, self._searching
        if hasattr(self, attr_name) or attr_name=='_searching' or  self._searching:
            return self.__getattr__(attr_name)
        else:
            print('search')
            self._searching = True
            try:
                obj = self[attr_name, 0] #tagging search
            except Exception:
                traceback.print_exc()
            self._searching = False
            if obj!=None:
                return obj
        return self.__getattr__(attr_name)#to throw exception
    '''