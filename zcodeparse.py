import re


def zlist(raw):
    """
    zlist provide similar function as list(), except for string.
    list("abc") returns ["a", "b", "c"] while zlist return ["abc"].
    """
    # 非迭代对象
    if not hasattr(raw, '__iter__'):
        return [raw]

    # 字符串对象
    if isinstance(raw, (bytes, str)):
        return [raw]

    # 其他可迭代对象
    return list(raw)

def with_function_style(class_):
    """
    This function decorate class with functional style.
    Instead of: "obj = class_(); obj(args);",
    now you can directly call "class_(args)" if class_ definition
    is already decorated by this function.
    """
    obj = class_()

    def wrapper(*args, **kwargs):
        return obj(*args, **kwargs)
    return wrapper


@with_function_style
class zcodeparse(object):
    """
    This class convert input codes (list-like) into
    codes with specified format.

    Example:
    # convert stk codes into output with format "600000.SH"
    v = ["600891","SZ000001","600001.SH",('0','600019')]
    print ParseStkCode(v,"600000.SH")

    Inside ParseStkCode, stk code are stored with format:("0","600000")
    """

    _instance = None

    # Stk Code Format
    # When adding new format, append new format in the end, and
    # add handle code for new format in __parse method
    _mode = "|".join(["^(SH|SZ|sh|sz){1}(00\d{4}|30\d{4}|15\d{4}|60\d{4}|51\d{4})",
                      "(00\d{4}|30\d{4}|15\d{4}|60\d{4}|51\d{4}).(SH|SZ|sh|sz){1}",
                      "(00\d{4}|30\d{4}|15\d{4}|60\d{4}|51\d{4})$"])

    _mapping_exch_mkt = {"SH": "0", "sh": "0", "SZ": "1", "sz": "1",
                         "0": "0", "1": "1"}

    def __new__(cls):
        "This class work in form of singleton"
        if cls._instance is None:
            cls._mode = re.compile(cls._mode)
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def __parse(self, code):
        """
        convert input code(str) into internal format: ("0","600000")
        """
        if isinstance(code, tuple):
            assert len(code) == 2
            exch_mkt, code_num = code
            assert exch_mkt in ['0', '1']
            if re.search("^(00\d{4}|30\d{4}|15\d{4}|60\d{4}|51\d{4})$", code_num):
                return exch_mkt, code_num
            else:
                raise Exception("Unkown Code Num: {}".format(code_num))

        elif isinstance(code, (str, bytes)):
            parsed_result = self._mode.search(code).groups()
            valid_parsed_result, valid_position =\
                self._filter_None(parsed_result)
            if valid_position == (0, 1):
                exch_mkt, code_num = valid_parsed_result
            elif valid_position == (2, 3):
                code_num, exch_mkt = valid_parsed_result
            elif valid_position == (4,):
                code_num, = valid_parsed_result
                exch_mkt = self._infer_exchmkt_bycode(code_num)
            else:
                raise Exception("Unknown Code Format.")
            exch_mkt = self._mapping_exch_mkt[exch_mkt]
            return exch_mkt, code_num

        else:
            raise Exception("Code type should be Tuple or Str")

    def __vparse(self, codes):
        """
        convert input codes(list-like) into internal format: ("0","600000")
        """
        if isinstance(codes, (tuple, str, bytes)):
            return self.__parse(codes)
        else:
            return list(map(lambda v: self.__parse(v), codes))

    def __format_reconstructcode(self, formatlike):
        """
        According to specified format, make corresponding function
        that converts internal codes (with format: ("0","600000"))
        into specified format.
        """
        if isinstance(formatlike, tuple):
            assert len(formatlike) == 2
            exch_mkt, code_num = formatlike
            assert exch_mkt in ['0', '1']
            if re.search("^(00\d{4}|30\d{4}|15\d{4}|60\d{4}|51\d{4})$", code_num):
                return lambda code: code
            else:
                raise Exception("Unkown Code Num: {}".format(code_num))
        elif isinstance(formatlike, (str, bytes)):
            parsed_result = self._mode.search(formatlike).groups()
            _, valid_position = self._filter_None(parsed_result)
            if valid_position == (0, 1):
                return lambda code: {"0": "SH", "1": "SZ"}[code[0]]+code[1]
            elif valid_position == (2, 3):
                return lambda code: code[1]+"."+{"0": "SH", "1": "SZ"}[code[0]]
            elif valid_position == (4,):
                return lambda code: code[1]

    def _infer_exchmkt_bycode(self, code_num):
        code_num = str(code_num)
        if code_num[:2] in ["00", "30", "15"]:
            return "SZ"
        elif code_num[:2] in ["60", "51"]:
            return "SH"
        else:
            raise Exception("Unknown Code Number.")

    def _filter_None(self, list_like):
        """
        This function filter all None value of input argument-list_like.
        And assert only One value is valid and return.
        """
        result = filter(lambda v: v[1] is not None, enumerate(list_like))
        result = list(zip(*result))
        return result[1], result[0]

    def __call__(self, codes, formatlike):
        # parse code, convert into internal format: ("0","600000")
        if isinstance(codes, (tuple, str, bytes)):
            codes = [codes]
        codes = self.__vparse(zlist(codes))
        # Convert internal codes into specified format
        format_func = self.__format_reconstructcode(formatlike)
        codes = list(map(format_func, codes))
        return codes[0] if len(codes) == 1 else codes


if __name__ == '__main__':
    codeformat1 = '600000.SH'
    codeformat2 = '600000'
    codeformat3 = 'SH600000'  # 天软
    codeformat4 = ('0', '600000') # 根网格式

    codes = ['601901.SH', '000002.SZ', '000009', 'SZ000001', ('1', '002356')]

    print(zcodeparse(codes, formatlike=codeformat4))

    print(zcodeparse('600000.SH', formatlike=codeformat4))

    # print(zcodeparse('601318.SH', ('0', '600000')))
    # print(zcodeparse(['601318.SH', '600030.SH', '000002.SZ'], 'SH600000'))
