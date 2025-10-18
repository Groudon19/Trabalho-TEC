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
        estados = set()
        for linha in linhas[1:]:
            if not linha.strip():
                continue
            x = padrao.match(linha)
            if not x:
                raise ValueError(f"Formato inválido na linha: {linha}")
            estado_atual, simbolo_lido, simbolo_escrito, direcao, proximo_estado = x.groups()
            estados.add(estado_atual)
            estados.add(proximo_estado)
            transicoes.append(Transicao(estado_atual, simbolo_lido, simbolo_escrito, direcao, proximo_estado))
    return cabecalho, transicoes, sorted(list(estados))

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
            
    elif cabecalho == ';I':
        
        with open(saida, 'w', encoding='utf-8') as arquivo_saida:
            nova_transicoes = []
            
            for t in transicoes:
                estado_atual = 'inicio' if t.estado_atual == '0' else t.estado_atual
                proximo_estado = 'inicio' if t.proximo_estado == '0' else t.proximo_estado
                nova_transicoes.append(Transicao(estado_atual, t.simbolo_lido, t.simbolo_escrito, t.direcao, proximo_estado))
            
            estados.remove('0')
            estados.append('inicio') 
            
            # Pré-processamento
            nova_transicoes.append(Transicao('0', '0', 'I', 'R', '1_0'))
            nova_transicoes.append(Transicao('0', '1', 'I', 'R', '1_1'))
            nova_transicoes.append(Transicao('0', '_', '*', '*', 'inicio'))
            
            nova_transicoes.append(Transicao('1_0', '0', '0', 'R', '1_0'))
            nova_transicoes.append(Transicao('1_0', '1', '0', 'R', '1_1'))
            nova_transicoes.append(Transicao('1_0', '_', '0', 'R', '1__'))
            
            nova_transicoes.append(Transicao('1_1', '0', '1', 'R', '1_0'))
            nova_transicoes.append(Transicao('1_1', '1', '1', 'R', '1_1'))
            nova_transicoes.append(Transicao('1_1', '_', '1', 'R', '1__'))
            
            nova_transicoes.append(Transicao('1__', '_', 'F', 'L', '2_'))
            
            nova_transicoes.append(Transicao('2_', 'I', 'I', 'R', 'inicio'))
            nova_transicoes.append(Transicao('2_', '*', '*', 'L', '2_'))
            
            # Tradução principal
            for e in estados:
                nova_transicoes.append(Transicao(e, 'I', 'I', 'R', 'q1___' + e))
                
                nova_transicoes.append(Transicao('q1_0_' + e, '0', '0', 'R', 'q1_0_' + e))
                nova_transicoes.append(Transicao('q1_0_' + e, '1', '0', 'R', 'q1_1_' + e))
                nova_transicoes.append(Transicao('q1_0_' + e, '_', '0', 'R', 'q1___' + e))
                nova_transicoes.append(Transicao('q1_0_' + e, 'F', '0', 'R', 'q1_F_' + e))
                
                nova_transicoes.append(Transicao('q1_1_' + e, '0', '1', 'R', 'q1_0_' + e))
                nova_transicoes.append(Transicao('q1_1_' + e, '1', '1', 'R', 'q1_1_' + e))
                nova_transicoes.append(Transicao('q1_1_' + e, '_', '1', 'R', 'q1___' + e))
                nova_transicoes.append(Transicao('q1_1_' + e, 'F', '1', 'R', 'q1_F_' + e))
                
                nova_transicoes.append(Transicao('q1___' + e, '0', '_', 'R', 'q1_0_' + e))
                nova_transicoes.append(Transicao('q1___' + e, '1', '_', 'R', 'q1_1_' + e))
                nova_transicoes.append(Transicao('q1___' + e, '_', '_', 'R', 'q1___' + e))
                nova_transicoes.append(Transicao('q1___' + e, 'F', '_', 'R', 'q1_F_' + e))
                
                nova_transicoes.append(Transicao('q1_F_' + e, '*', 'F', 'l', 'q2' + e))
                
                nova_transicoes.append(Transicao('q2' + e, '*', '*', 'l', 'q2' + e))
                nova_transicoes.append(Transicao('q2' + e, 'I', 'I', 'r', e))
                
                nova_transicoes.append(Transicao(e, 'F', '_', 'r', 'q_F' + e))
                nova_transicoes.append(Transicao('q_F' + e, '*', 'F', 'l', e))
                
            for t in nova_transicoes:
                arquivo_saida.write(f" {t.estado_atual} {t.simbolo_lido} {t.simbolo_escrito} {t.direcao} {t.proximo_estado} \n")
        
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