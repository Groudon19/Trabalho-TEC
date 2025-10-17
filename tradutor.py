import sys
import os
import re
from collections import namedtuple

Transicao = namedtuple('Transicao', ['estado_atual', 'simbolo_lido', 'simbolo_escrito', 'direcao', 'proximo_estado'])

def extrai_transicoes(caminho):
    
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        linhas = [ln.rstrip('\n') for ln in arquivo]
        padrao = re.compile(r'^\s*(\S+)\s+(\S+)\s+(\S+)\s+([LlRr\*])\s+(\S+)\s*$')
        if not linhas:
            raise ValueError("Arquivo vazio")
        cabecalho = linhas[0].strip()
        if cabecalho not in [';S',';I']:
            raise ValueError("Deve começar com ;S ou ;I")
        transicoes = []
        estados = []
        for linha in linhas[1:]:
            if not linha.strip():
                continue
            x = padrao.match(linha)
            if not x:
                raise ValueError(f"Formato inválido na linha: {linha}")
            estado_atual, simbolo_lido, simbolo_escrito, direcao, proximo_estado = x.groups()
            if estado_atual not in estados:
                estados.append(estado_atual)
            transicoes.append(Transicao(estado_atual, simbolo_lido, simbolo_escrito, direcao, proximo_estado))
    return cabecalho, transicoes, estados

def _saida_para_entrada(caminho):
    root, ext = os.path.splitext(caminho)
    if ext.lower() == '.in':
        return root + '.out'
    return caminho + '.out'

def traduzir_mt(caminho):
    
    cabecalho, transicoes, estados = extrai_transicoes(caminho)
    saida = _saida_para_entrada(caminho)
    if cabecalho == ';S':
        with open(saida, 'w', encoding='utf-8') as arquivo_saida:
            nova_transicoes = []
            
            for t in transicoes:
                estado_atual = 'inicio' if t.estado_atual == '0' else t.estado_atual
                proximo_estado = 'inicio' if t.proximo_estado == '0' else t.proximo_estado
                nova_transicoes.append(Transicao(estado_atual, t.simbolo_lido, t.simbolo_escrito, t.direcao, proximo_estado))
            
            for e in estados:
                e_mapeado = 'inicio' if e == '0' else e
                nova_transicoes.append(Transicao(e_mapeado, 'M', 'M', 'R', e_mapeado))
                
            nova_transicoes.append(Transicao('0', '*', '*', 'L', 'mola'))
            nova_transicoes.append(Transicao('mola', '*', 'M', 'R', 'inicio'))
            
            for t in nova_transicoes:
                arquivo_saida.write(f" {t.estado_atual} {t.simbolo_lido} {t.simbolo_escrito} {t.direcao} {t.proximo_estado} \n")
            
    # elif cabecalho == ';I':
        
    else:
        raise ValueError("Cabeçalho deve ser ;S ou ;I")
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python tradutor.py <caminho_para_arquivo_de_entrada>")
        sys.exit(1)
    
    caminho_arquivo = sys.argv[1]
    try:
        traduzir_mt(caminho_arquivo)
        print("Tradução concluída com sucesso.")
    except Exception as e:
        print(f"Erro durante a tradução: {e}")
        sys.exit(1)