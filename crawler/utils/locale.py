import regex as re

regex_japanese = r'[\p{Hiragana}\p{Katakana}]+'
regex_chinese = r'[\p{InCJK_Unified_Ideographs}\p{InCJK_Unified_Ideographs_Extension_A}\p{InCJK_Compatibility}]+'
regex_korean = r'[\p{InHangul_Compatibility_Jamo}\p{InHangul_Syllables}]+'


def classify_locale(str):
    k = c = j = e = 0
    lines = str.split('\n')
    for line in lines:
        if re.search(regex_korean, line, re.U):
            k += 1
        elif re.search(regex_japanese, line, re.U):
            j += 1
        elif re.search(regex_chinese, line, re.U):
            c += 1
        else:
            e += 1

    max_locale = max(k,c,j,e)
    if max_locale == k:
        return 'korean'
    elif max_locale == c:
        return 'chinese'
    elif max_locale == j:
        return 'japanese'
    else:
        return 'english'
