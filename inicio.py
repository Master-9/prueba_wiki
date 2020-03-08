import sys
import requests
import re
import os
import json
import xml
import itertools
import io
import cProfile
import ujson
import time
import timeit
import lxml
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

URL = 'https://es.wikipedia.org/w/api.php'
# tt = 'srwhat': "text"
CLAVE = "llevar"
PARAMS = {'action': "query",
          'list': "search",
          'format': "json",
          'srwhat': "text",
          'utf8': "",
          'srlimit': '100',
          'srsearch': '{} insource:/"{}"/'.format(CLAVE, CLAVE)}

SUSTITUCIONES = {'\n': '', '&quot;': '', '&gt;': '', '&lt;': ''}
PUNTOS0 = re.compile(r'.*\.|\|{1}|\]{1,}|\[{1,}|\{{1,}|\}{1,}|={1,}|\'|\"')
PUNTOS2 = re.compile(r'\..*|\|{1}|\]{1,}|\[{1,}|\{{1,}|\}{1,}|={1,}|\'|\"')


def main(*args):
    module = sys.modules[__name__]

    inicio_tiempo = time.perf_counter_ns()
    # get_optimized()
    fin_tiempo = time.perf_counter_ns()
    # print("\n----------------\n")

    inicio_tiempo1 = time.perf_counter_ns()
    # get()
    #get_document()
    anotar_corenlp()
    fin_tiempo1 = time.perf_counter_ns()
    tiempo = fin_tiempo - inicio_tiempo
    tiempo1 = fin_tiempo1 - inicio_tiempo1
    print(tiempo / 1000000000, tiempo1 / 1000000000, "ms")

    #doIt()


def doIt():
    s = 'actual es la implementación de   ¿políticas de ¡asistencia!, social pero de ninguna manera?. cambiar el sistema económicoltref; namequotcfquotgtSegún: Rawls'
    print(s)
    a = "el encontro. hghsfj."
    #print(re.sub(re.compile(r'\..*'), '', a))
    if re.search('[^\w\s,;.!?¿:¡]', s) is None:
        print(a)
    else:
        print(s)


def susti_puntoss(subcadena, rep, patron, puntos0=PUNTOS0, puntos2=PUNTOS2):

    return (re.sub(puntos0, ' ', swap_multiples_string1(subcadena[0], rep, patron)), subcadena[1],
    re.sub(puntos2, ' ', swap_multiples_string1(subcadena[2], rep, patron)))


def susti_puntos(subcadena, ind):

    if ind == 0:
        puntos = re.compile(r'.*\.|\|{1}|\]{1,}|\[{1,}|\{{1,}|\}{1,}|={1,}|\'|\"')
    elif ind == 2:
        puntos = re.compile(r'\..*|\|{1}|\]{1,}|\[{1,}|\{{1,}|\}{1,}|={1,}|\'|\"')
    else:
        return subcadena
    return re.sub(puntos, ' ', swap_multiples_string(subcadena))


def swap_multiples_string1(cadena, rep, patron, reemplazos=SUSTITUCIONES):
    # rep = dict((re.escape(old), new) for old, new in reemplazos.items())
    # patron = re.compile("|".join(reemplazos.keys()))
    return patron.sub(lambda match: rep[re.escape(match.group(0))], cadena)


def swap_multiples_string(cadena, reemplazos=SUSTITUCIONES):
    rep = dict((re.escape(old), new) for old, new in reemplazos.items())
    patron = re.compile("|".join(reemplazos.keys()))
    return patron.sub(lambda match: rep[re.escape(match.group(0))], cadena)


def get_optimized(una_url=URL):  # LENTO
    ses = requests.Session()
    response = ses.get(una_url, params=PARAMS)
    response.raise_for_status()

    pp = re.compile(r'\<span\s{1}class=\"searchmatch\"\>|\<\/span\>')
    #hay = [re.split(pp, dato["snippet"]) for dato in ujson.loads(response.text)["query"]["search"]]

    #for adr in hay:
        #print(adr)

    json_data = response.json()
    rep = dict((re.escape(old), new) for old, new in SUSTITUCIONES.items())
    patron = re.compile("|".join(SUSTITUCIONES.keys()))

    #d = json_data["query"]["search"]  # lista de diccionarios

    #print(next(map(lambda tupla: susti_puntos(tupla[1], tupla[0]), enumerate(tup)) for tup
     #                      in (re.split(pp, dato["snippet"]) for dato in json_data["query"]["search"]) ))

    arr = [{res[1]: ''.join(res).strip()} for res in (susti_puntoss(tup, rep, patron) for tup in
                            (re.split(pp, dato["snippet"]) for dato in json_data["query"]["search"]) ) if re.
                    search('[^\w\s,;.!?¿:¡]', ''.join(res)) is None]
    #arr = [{tup[1]: ''.join(tup)}  for tup in
           #(re.split(pp, dato["snippet"]) for dato in json_data["query"]["search"]) ]
    #for oracion in arr:
        #print(oracion)
    #print("\n----------------\n")


def separar(row):
    des = None
    sep = re.compile(r'\. |\.\n|[;:]')
    conjunto = []
    if '¡' in row or '¿' in row:
        un_row = row
        patt_unido = re.compile(r'¡.+?!|¿.+?\?')
        ros = re.split(patt_unido, un_row)  # retorna las partes que no pertenecen a una exclamacion
        des = re.findall(patt_unido, un_row)
        if ros != ['', '']:  # la parte no exclamativa y/o no interrogativa no es nula
            for ro in ros:
                if ro != '':
                    [conjunto.append(aa.strip(' -').replace('\n', '')) for aa in re.split(
                        sep, ro) if aa != '' and aa != ' ' and aa != '-' and aa != ' -' and aa != ', ']
        res = conjunto + des if conjunto != [] else des
        # print('res*', res, len(res))
        # for i, unn in enumerate(res):
        #    print(unn, i)
        #    z = sys.stdin.readline().strip('\n')
        #    if z != '':
        #       res[i] = z
        return res  # entre_signos(row, sep, ['¿', '!'])
    else:
        a = [aa.strip(' -').replace('\n', '') for aa in re.split(sep, row) if aa != '']
        # print('a*', a, len(a))
        return a


def anotar_corenlp(oracion="La policía emprendió la investigación poco antes del verano"):

    propiedades = {
        "serverProperties": "StanfordCoreNLP-spanish.properties",
        "annotators": "tokenize, ssplit, pos, depparse",
        "outputFormat": "json"
    }

    res = requests.post(url='http://[::]:9000?properties={}'.format(propiedades),
                  data=oracion.encode(encoding='utf-8'))
    #res = requests.post('http://[::]:9000/?properties={"annotators":"tokenize,ssplit,pos, depparse","outputFormat":"json"}',
    #                    data={'data': oracion})
    res.raise_for_status()
    sal = res.json()
    print(json.dumps(sal, indent=4, ensure_ascii=False))

def encontrar_pal(palabra, texto):
    """ \b Matches the empty string, but only at the beginning or end of a word """
    char_no_pal = r'\W{1}'
    pat1 = re.compile(r'^{}{}|{}{}$|{}{}{}'.format(
        palabra, char_no_pal, char_no_pal, palabra, char_no_pal, palabra, char_no_pal))
    pat2 = re.compile(r'\b{}\b'.format(palabra))
    return re.search(pat2, texto)




def beautiful_parser(root):
    bs = BeautifulSoup(ET.tostring(root), 'xml')
    ejemplos = bs.find_all('text')
    tot = []
    for ejemplo in ejemplos:
        tot += separar(ejemplo.getText())
    return tot


def get_document(path='spanish_corpus/'):
    nom = 'elpais_es_corpus_xml'
    arbol = ET.parse("{}.xml".format(nom))
    root = arbol.getroot()
    textos = beautiful_parser(root)
    print(textos, len(textos))
    calls = None
    with open('objetivos.txt', 'r') as q:
        calls = {arr[0]: arr[1] for arr in (lin.split('; frame:') for lin in q)}
    targets = dict()
    for texto in textos:
        for call in calls.keys():
            var = encontrar_pal(call, texto)
            if var is not None:
                if targets.get(call) is None:
                    targets[call] = []
                    targets[call].append(texto)
                else:
                    targets[call].append(texto)
    for target in targets.keys():
        with open('data_abc/' + target + '.txt', 'a') as arc:
            for un in targets[target]:
                arc.write(str(un) + '\n')


    for file in os.listdir(path):
        if file.startswith("spanishText_"):
            pass


def get(una_url=URL):
    ses = requests.Session()
    #with open('objetivos.txt', 'r') as q:
    #    calls = {arr[0]: arr[1] for arr in (lin.split('; frame:') for lin in q)}

    calls = {'qué es': 'val'}
    for call in calls.keys():
        query = '"sino".*"porque"'
        par = {'action': "query",
               'list': "search",
               'format': "json",
               'srwhat': "text",
               'utf8': "",
               'srlimit': '1000',
               'srsearch': '{} insource:/{}/'.format(query, query)}
                # 'srsearch': '{} insource:/"{}"/'.format(query, query)}
        print(par['srsearch'])
        response = ses.get(una_url, params=par)
        response.raise_for_status()

        #[map(lambda tupla: susti_puntos(tupla[1], tupla[0]), enumerate(tup)) for tup in (re.split(pp, dato["snippet"]) for dato in json_data["query"]["search"])]
        json_data = response.json()
        pp = re.compile(r'\<span\s{1}class=\"searchmatch\"\>|\<\/span\>')

        arr = [{res[1]: ''.join(res).strip()} for res in (tuple(terna) for terna in
                            [map(lambda tupla: susti_puntos(tupla[1], tupla[0]), enumerate(tup)) for tup in
                             (re.split(pp, dato["snippet"]) for dato in
                              json_data["query"]["search"])]) if re.search('[^\w\s,;.!?¿:¡]', ''.join(res)) is None]
        #arr = [{tup[1]: ''.join(tup)}  for tup in
               #(re.split(pp, dato["snippet"]) for dato in json_data["query"]["search"]) ]


        #with open('data/' + query + '.txt', 'a') as arc:
        #    for oracion in arr:
        #        arc.write(str(oracion) + '\n')


        for oracion in arr:
            print(oracion)
        #print("\n----------------\n")
        #print(json.dumps(json_data, ensure_ascii=False, indent=4))

        #bs = BeautifulSoup(response.text, 'html.parser')
        #print(bs.prettify())

def example():
    for d in range(1000):
        e = 3+4


if __name__ == '__main__':
    import timeit
    # t = timeit.timeit("get_optimized()", setup="import requests, re; from __main__ import susti_puntos, SUSTITUCIONES, URL, PARAMS, get ",number=10)
    # t = timeit.timeit("get_optimized()",
                      #setup="import requests, re; from __main__ import susti_puntoss, SUSTITUCIONES, URL, PARAMS, "
                            #"PUNTOS0, PUNTOS2, swap_multiples_string1, get_optimized", number=10)
    # print(t/10)
    # print(timeit.timeit("example()", setup="from __main__ import example"))
    main(*sys.argv[1:])