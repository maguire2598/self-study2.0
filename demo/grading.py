"""Conservative answer checking without expression evaluation."""
import re
import unicodedata
from fractions import Fraction

def normalize(text):
    return ''.join(unicodedata.normalize('NFKC', text).replace('−', '-').split())

def numeric(text):
    if len(text) > 100 or not re.fullmatch(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:/[+-]?\d+)?', text):
        return None
    try:
        return Fraction(text)
    except (ValueError, ZeroDivisionError):
        return None

def grade(question, answers):
    if question['question_type'] != 'multi_blank':
        valid = {o['id'] for o in question['options']}
        if (not isinstance(answers, list) or not answers or any(not isinstance(a, str) for a in answers)
                or len(set(answers)) != len(answers) or not set(answers) <= valid
                or (question['question_type'] == 'single_choice' and len(answers) != 1)):
            raise ValueError('请选择有效选项，且不要重复提交选项。')
        return set(answers) == set(question['correct_answers'])
    if not isinstance(answers, dict) or set(answers) != {b['id'] for b in question['blanks']}:
        raise ValueError('请填写全部空格。')
    result = True
    for blank in question['blanks']:
        raw = answers[blank['id']]
        if not isinstance(raw, str) or not raw.strip() or len(raw) > 1000:
            raise ValueError('每个空格需要有效文字。')
        value = normalize(raw)
        if value.lower() in {'nan', 'inf', '+inf', '-inf', 'infinity', '+infinity', '-infinity'}:
            raise ValueError('请输入有限数值或文字。')
        accepted = [normalize(a) for a in blank['accepted_answers']]
        number = numeric(value)
        result &= value in accepted or (number is not None and any(number == numeric(a) for a in accepted))
    return bool(result)
