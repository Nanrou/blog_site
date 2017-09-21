from string import digits

mol_dict = {
    '10': 'a',
    '11': 'b',
    '12': 'c',
    '13': 'd',
    '14': 'e',
    '15': 'f',
}

dex_dict = {
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15,
}



def pro_hex(start, stop):
    _range = []
    for _num in [start, stop]:  # 将16位转回10位
        _n = 0
        for i in _num:
            if i not in digits:
                i = dex_dict[i]
            _n = _n *16 + int(i)
        _range.append(_n)
    _start, _stop = _range
    for i in range(_start, _stop+1):
        result = ''
        while i:  # 逐位取模来拿到每一位的值
            mol_num = str(i % 16)
            result = (mol_dict[mol_num] if mol_num in mol_dict else mol_num ) + result
            # print('mol: {}, result: {}'.format(mol_num, result))
            i = i // 16
        yield result

if __name__ == '__main__':
    import sys
    for i in pro_hex('1', '16'):
        print(i)
    
                