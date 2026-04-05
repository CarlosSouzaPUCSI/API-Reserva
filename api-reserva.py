# Precisa importar todas as bibliotecas e funções que vão ser usadas
from fastapi import FastAPI, status, HTTPException, Depends
from schema import reservaEntrada, reservaEdicao
from model import reservas
from typing import Optional
from database import criarSessao
from sqlmodel import Session, select

# Criando a instância da aplicação com o FastAPI
appReserva = FastAPI() # Define o nome da variável que chamará a aplicação, se eu alterar tem que alterar em cada rota e no arquivo pyproject.toml

# Criando as rotas que definirão as ações
# Rota de criação da reserva 
@appReserva.post("/reserva", status_code=status.HTTP_201_CREATED) # (, xyz) -> entrega status se não houver levantamento de erro durante a execução
def criarReserva(dadosEntrada: reservaEntrada, sessao: Session = Depends(criarSessao)): # (X:Y) -> o que receberá será armazenado na variável X e deverá ter o formato Y
    # Regra de negocio: saber se já existe uma reserva com o a mesma sala que coincida com o horario entregue mesmo que parcialmente
    query = select(reservas).where( # monta a query pro banco
        reservas.id_sala == dadosEntrada.id_sala, # puxa tudo que tiver a sala que recebi
        reservas.entrada < dadosEntrada.saida, # tudo que tiver entrada anterior a saida que recebi
        reservas.saida > dadosEntrada.entrada # tudo que tiver saida posterior a entrada que recebi, com isso garanto que pega tudo que intercepte esse intervalo
        ) 
    existe = sessao.exec(query).first() # executa e busca a primeira relação, pois se tiver 1 ou 10 iguais tá errado igual, então se achar 1 já poupa de percorrer o resto da tabela
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A sala já está ocupada neste horário")
    
    # converter os dados para o modelo
    novaReserva = reservas(**dadosEntrada.model_dump()) 
    
    # criar a reserva no banco
    sessao.add(novaReserva) # prepara o objeto pra escrever
    sessao.commit() # escreve no banco o que ta pendente

    # buscar o objeto pelas infos da entrada la no banco pra mostrar
    sessao.refresh(novaReserva) # busca a versão atualizada do que enviei e salva (ou seja, vem com o que é resolvido no modelo e no banco)

    return novaReserva # retorna o objeto criado junto com o codigo

# # Rota de listagens 
# # Todas as reservas
# @appReserva.get("/reserva", status_code=status.HTTP_200_OK)
# def listarReservas(id_cliente: Optional[int] = None, id_sala: Optional[int] = None ): # Ainda precisa entregar a sessao do banco
#     listaReservas = ... # pegar a lista de todas as reservas 
#     return listaReservas # retorna a lista com tudo

# # Uma reserva específica
# @appReserva.get("/reserva/{id}", status_code=status.HTTP_200_OK)
# def listarReservas(id: int):
#     encontrado = False
#     index = -1

#     for item in listaReservas: # Looping checando todos os itens
#         index += 1 # Cada item checado adiciona um pra equivaler ao index
#         if item.id == id: # checa se é o que quero
#             encontrado = True # muda se achar
#             break # para o looping assim que achar pra não procurar atoa

#     if encontrado == False: 
#         raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
#     return listaReservas[index] # Terá muito mais complexidade quanto eu colocar o banco, pois terei que buscar nele as informações

# # Rota para edição de reservas ( talvez não faça sentido diretamente no negócio mas entendo ser ok de implementar pelo caso de um dia ser necessário e então já ter ) / Perguntar se preciso de fazer essa separação, pq se for olhar se eu usar Patch e entregar todos os dados já faz o efeito do put
# # Alterar completamente
# @appReserva.put("/reserva/{id}", status_code=status.HTTP_200_OK)
# def editarTudo(editarReserva: reserva):
#     encontrado = False
#     index = -1

#     for item in listaReservas:
#         index += 1
#         if item.id == editarReserva.id:
#             encontrado = True
#             break
#     if encontrado == False:
#         raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
#     reservaEditada = reserva(
#         id = editarReserva.id,
#         id_cliente = editarReserva.id_cliente,
#         id_sala = editarReserva.id_sala,
#         status = editarReserva.status,
#         feito_em = editarReserva.feito_em,
#         entrada = editarReserva.entrada,
#         saida = editarReserva.saida
#     )

#     del listaReservas[index] # Deleta o item do index indicado
#     listaReservas.append(reservaEditada) 

#     return listaReservas[-1]

# # Informações específicas
# @appReserva.patch("/reserva/{id}", status_code=status.HTTP_200_OK)
# def editar(editarReserva: reservaEdicao):
#     encontrado = False
#     index = -1

#     for item in listaReservas:
#         index += 1
#         if item.id == editarReserva.id:
#             encontrado = True
#             break
#     if encontrado == False:
#         raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
#     reservaAntiga = listaReservas[index] # defino o que já existe em uma variável, pelo que entendi, por ser objeto a variável vira uma referência do item dentro da lista e não uma cópia como seria com um int ou str, então ao editar "a variável" eu estou editando na vdd o item da lista

#     novosDados = editarReserva.model_dump(exclude_unset=True) # pego a entrada e excluo todos os itens nulos e só sobram atributos que vão ser modificados, e o id, no objeto

#     for atributo, valor in novosDados.items(): # percorre todos os atributos que sobraram da entrada
#         if atributo == "id":
#             continue # pula o id para evitar processamento desnecessário

#         setattr(reservaAntiga, atributo, valor) # Equiparado a objeto.nome = valor, mas como nesse caso o atributo do for é uma str então preciso entregar para essa função

#     return listaReservas[index]

# # Rota para exclusão de reservas ( talvez não faça sentido diretamente no negócio mas entendo ser ok de implementar pelo caso de um dia ser necessário e então já ter )
# # Todas as reservas 
# @appReserva.delete("/reserva", status_code=status.HTTP_204_NO_CONTENT)
# def deletarTudo():
#     listaReservas.clear()
#     return

# # Uma reserva específica
# @appReserva.delete("/reserva/{id}", status_code=status.HTTP_204_NO_CONTENT)
# def deletarUm(id: int):
#     encontrado = False
#     index = -1

#     for item in listaReservas:
#         index += 1
#         if item.id == id:
#             encontrado = True
#             break
#     if encontrado == False:
#         raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
#     del listaReservas[index]

#     return # Terá mais complexidade quanto eu colocar o banco, pois terei que buscar nele as informações