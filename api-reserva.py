# Precisa importar todas as bibliotecas e funções que vão ser usadas
from fastapi import FastAPI, status, HTTPException, Depends, Query
from schema import reservaEntrada, reservaEdicao
from model import reservas, cliente, sala
from typing import Optional
from database import criarSessao
from sqlmodel import Session, select
from sqlalchemy import func
from datetime import datetime, date
from zoneinfo import ZoneInfo
from funcoes import verificar

# Criando a instância da aplicação com o FastAPI
appReserva = FastAPI() # Define o nome da variável que chamará a aplicação, se eu alterar tem que alterar em cada rota e no arquivo pyproject.toml

# Criando as rotas que definirão as ações
# Rota de criação da reserva 
@appReserva.post("/api/reserva", status_code=status.HTTP_201_CREATED) # (, xyz) -> entrega status se não houver levantamento de erro durante a execução
def criarReserva( 
    dadosEntrada: reservaEntrada, # (X:Y) -> o que receberá será armazenado na variável X e deverá ter o formato Y
    sessao: Session = Depends(criarSessao) # Cria a sessão com o banco e diz que depende da minha função, isso força o encerramento quando acabar essa função
    )  -> reservas: # -> diz o que vai entregar no fim da função, ajuda o openapi a montar a documentação
    # Criando a função de gerar o tempo
    agora = lambda: datetime.now(ZoneInfo("America/Sao_Paulo"))
    
    # Garantir limpeza
    verificar(cliente, dadosEntrada.id_cliente, sessao) # verifica se existe o que to informando e já cria o erro se não existir
    verificar(sala, dadosEntrada.id_sala, sessao)

    if dadosEntrada.entrada >= dadosEntrada.saida:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A entrada fornecida é igual ou após a saída")
    
    if dadosEntrada.entrada <= agora():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A reserva não pode ser criada no passado")
    
    # Regra de negocio: impedir reservas sejam feitas em horários quebrados
    if dadosEntrada.entrada.minute != 0 or dadosEntrada.saida.minute != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A hora de entrada e saída devem ser horas inteiras (exemplo: 10:00)")

    # Regra de negocio: as reservas nao podem passar de dia, data de entrada = data de saida
    if dadosEntrada.entrada.date() != dadosEntrada.saida.date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de entrada difere da data de saída.")

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
    sessao.refresh(novaReserva) # busca a versão atualizada do que enviei e salva (ou seja, vem com o que é resolvido no modelo e no banco)

    return novaReserva # retorna o objeto criado junto com o codigo

# Rota de listagens 
# Todas as reservas, com filtro de cliente, sala ou data
@appReserva.get("/api/reserva", status_code=status.HTTP_200_OK)
def listarReserva( # preciso listar tudo, pois método get não pode ter corpo, se eu usar schema, ele pede um objeto no corpo
    id_cliente: Optional[int] = None, # Com esse default em None não preciso criar 4 rotas, o que não forcer eu não faço
    id_sala: Optional[int] = None, # Se fornecer mais de um, só vai incrementar o filtro
    inicio: Optional[date] = None,
    fim: Optional[date] = None, # Se não fornecer nenhum entrega todas as reservas
    offset: int = 0, # Se for carregar pagina 2 vai me entregar valor, se nao, é os primeiros valores
    limit: int = Query(default= 10, le= 100), # limita para proteger a memoria, se nao entregar, lista 10, se entregar mais que 100, muda pra 100 
    sessao: Session = Depends(criarSessao)
    ) -> list[reservas]: 
    # Garantir limpeza
    if bool(inicio) ^ bool(fim):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se fornecer inicio ou fim, deve fornecer o outro.")
    
    # criar as variável que vou precisar 
    query = select(reservas)

    # implementando os filtros
    if id_cliente:
        verificar(cliente, id_cliente, sessao) # verifico só se me entregar
        query = query.where(reservas.id_cliente == id_cliente)

    if id_sala:
        verificar(sala, id_sala, sessao)
        query = query.where(reservas.id_sala == id_sala)

    if inicio and fim:
        query = query.where(
            func.date(reservas.entrada) >= inicio,
            func.date(reservas.entrada) <= fim
            )
    
    # Fazer a busca 
    listaReservas = sessao.exec(query.offset(offset).limit(limit)).all()

    return listaReservas # retorna a lista com tudo

# Uma reserva específica
@appReserva.get("/api/reserva/{id}", status_code=status.HTTP_200_OK)
def buscarReserva(
    id: int,
    sessao: Session = Depends(criarSessao)
    ) -> reservas:
    # busco no banco
    objeto = verificar(reservas, id, sessao) # essa funcao verifica e devolve o objeto se existir  

    return objeto

# # Rota para edição de reservas ( talvez não faça sentido diretamente no negócio mas entendo ser ok de implementar pelo caso de um dia ser necessário e então já ter ) / Perguntar se preciso de fazer essa separação, pq se for olhar se eu usar Patch e entregar todos os dados já faz o efeito do put
# # Alterar completamente
# @appReserva.put("/api/reserva/{id}", status_code=status.HTTP_200_OK)
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
# @appReserva.patch("/api/reserva/{id}", status_code=status.HTTP_200_OK)
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
# @appReserva.delete("/api/reserva", status_code=status.HTTP_204_NO_CONTENT)
# def deletarTudo():
#     listaReservas.clear()
#     return

# # Uma reserva específica
# @appReserva.delete("/api/reserva/{id}", status_code=status.HTTP_204_NO_CONTENT)
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