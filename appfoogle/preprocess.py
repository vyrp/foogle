# -*- coding: utf-8 -*-

import re

_commonWords = re.compile(ur"^(por|pel[oa]s?|ao?s?|d[aeo]s?|duma?s?|em|nas?|entre|com|sem|os?|ou|se|que|for|at|the|and|or|in|that|by)$")

_equivalents = {
    'voce': 'vc',
    'porque': 'pq',
    'abraco': 'abc',
    'beijo': 'bj',
    'beijos': 'bj',
    'bjos': 'bj',
    'beijao': 'bj',
    'bjao': 'bj',
    'comigo': 'cmg',
    'contigo': 'ctg',
    'quando': 'qdo',
    'qndo': 'qdo',
    'favor': 'pf',
    'muito': 'mt',
    'mto': 'mt',
    'tambem': 'tb',
    'tbm': 'tb',
    'estao': 'tao',
    'esta': 'ta',
    'estou': 'to',
    'como': 'cm',
    'qualquer': 'qlquer',
    'gente': 'gt',
    'gte': 'gt',
    'gnte': 'gt',
    'depois': 'dpois',
    'obrigado': 'brigado',
    'obrigada': 'brigada',
    'hoje': 'hj',
    'beleza': 'blz',
    'cara': 'kra',
    'valeu': 'vlw',
    'falou': 'flw',
    'adicionar': 'add',
    'certeza': 'ctz',
    'cerveja': 'crvja',
    'dica': 'dik',
    'cade': 'kd',
    'kde': 'kd',
    'abracos': 'abs',
    'tchau': 'xau',
    'mensagem': 'msg',
    'mesmo': 'msm',
    'apartamento': 'apt',
    'apto': 'apt',
    'agora': 'agr',
    'aqui': 'aki',
    'aquilo': 'akilo',
    'aquele': 'akele',
    'aquela': 'akela',
    'alguem': 'algm',
    'acho': 'axo',
    'casa': 'ksa',
    'depois': 'dpois',
    'enquanto': 'enqto',
    'entaum': 'entao',
    'naum': 'n',
    'nao': 'n',
    'fica': 'fik',
    'horas': 'hr',
    'hora': 'hr',
    'hrs': 'hr',
    'jah': 'ja',
    'cabeca': 'kbca',
    'imagina': 'magina',
    'amigo': 'migo',
    'amiga': 'miga',
    'migs': 'miga',
    'moleque': 'mlq',
    'mlk': 'mlq',
    'nada': 'nd',
    'ninguem': 'ng',
    'ngm': 'ng',
    'aniversario': 'niver',
    'numero': 'nr',
    'num': 'nr',
    'nunca': 'nunk',
    'para': 'pra',
    'espera': 'pera',
    'qualquer': 'qlqr',
    'qlquer': 'qlqr',
    'quero': 'qro',
    'quase': 'qse',
    'quantidade': 'qtd',
    'qtde': 'qtd',
    'quanto': 'qto',
    'verdade': 'vdd',
    'valeu': 'vlw',
    'vezes': 'vzs',
    'vou': 'vo',
    'com': 'c',
    'sim': 's',
    'que': 'q',
    'macho': 'mah',
    'vixe': 'vish',
    'depois': 'dpois',
    'qual': 'ql',
    'notebook': 'note',
    'facebook': 'fb',
    'te': 't'
};

def _normalize(word):
    word = word.lower()
    word = re.sub(ur'[áâàãä]', r'a', word)
    word = re.sub(ur'[éêèë]', r'e', word)
    word = re.sub(ur'[íîìï]', r'i', word)
    word = re.sub(ur'[óôòõö]', r'o', word)
    word = re.sub(ur'[úûùü]', r'u', word)
    word = re.sub(ur'[ýÿ]', r'y', word)
    word = re.sub(ur'ç', r'c', word)
    word = re.sub(ur'ñ', r'n', word)
    word = re.sub(ur'^[^a-zA-Z0-9]+', r'', word)
    word = re.sub(ur'[^a-zA-Z0-9]+$', r'', word)
    # word = re.sub(ur'[^a-zA-Z0-9]', r'', word)
    return word

def _simplify(word):
    if word in _equivalents:
        return _equivalents[word]
    return word

def _isCommon(word):
    return bool(_commonWords.match(word))

def preprocess(word):
    word = _normalize(word)
    if _isCommon(word):
        return ""
    return _simplify(word)
