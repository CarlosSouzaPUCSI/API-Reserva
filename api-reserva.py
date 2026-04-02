# Precisa importar todas as bibliotecas e funções que vão ser usadas
from fastapi import FastAPI, status, HTTPException
from schema import reserva, reservaEntrada, reservaEdicao

# Criando a instância da aplicação com o FastAPI
appReserva = FastAPI() # Define o nome da variável que chamará a aplicação, se eu alterar tem que alterar em cada rota e no arquivo pyproject.toml

# Definir coisas para simular o banco por enquanto
listaReservas = []
contadorId = 1

# Criando as rotas que definirão as ações
# Rota de criação da reserva 
@appReserva.post("/reserva", status_code=status.HTTP_201_CREATED) # (, xyz) -> entrega status se não houver levantamento de erro durante a execução
def criarReserva(reservaEntrada: reservaEntrada): # (X:Y) -> o que receberá será armazenado na variável X e deverá ter o formato Y ( definido no Schema )
    global contadorId # Declarando a variável criada fora da função pois tenho interesse em alterá-la
    novaReserva = reserva( # Cria uma varíavel que é um objeto do tipo reserva, definido no schema
        id = contadorId,
        id_cliente = reservaEntrada.id_cliente,
        id_sala = reservaEntrada.id_sala,
        status = "Confirmada",
        entrada = reservaEntrada.entrada,
        saida = reservaEntrada.saida
    )
    listaReservas.append(novaReserva) # Adicinando no banco fake
    contadorId += 1 # Fakeando serial
    return listaReservas[-1] # Entrega a útltima reserva da lista, isso é problemático quando a lista não tem valores, mas como acabou de criar ta de boa

# Rota de listagens / Perguntar se preciso de fazer essa separação, pq se for olhar se eu usar Patch e entregar todos os dados já faz o efeito do put
# Todas as reservas
@appReserva.get("/reserva", status_code=status.HTTP_200_OK)
def listarReservas():
    return listaReservas # Terá muito mais complexidade quanto eu colocar o banco, pois terei que buscar nele as informações

# Uma reserva específica
@appReserva.get("/reserva/{id}", status_code=status.HTTP_200_OK)
def listarReservas(id: int):
    encontrado = False
    index = -1

    for item in listaReservas: # Looping checando todos os itens
        index += 1 # Cada item checado adiciona um pra equivaler ao index
        if item.id == id: # checa se é o que quero
            encontrado = True # muda se achar
            break # para o looping assim que achar pra não procurar atoa

    if encontrado == False: 
        raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
    return listaReservas[index] # Terá muito mais complexidade quanto eu colocar o banco, pois terei que buscar nele as informações

# Rota para edição de reservas ( talvez não faça sentido diretamente no negócio mas entendo ser ok de implementar pelo caso de um dia ser necessário e então já ter )
# Alterar completamente
@appReserva.put("/reserva", status_code=status.HTTP_200_OK)
def editarTudo(editarReserva: reserva):
    encontrado = False
    index = -1

    for item in listaReservas:
        index += 1
        if item.id == editarReserva.id:
            encontrado = True
            break
    if encontrado == False:
        raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
    reservaEditada = reserva(
        id = editarReserva.id,
        id_cliente = editarReserva.id_cliente,
        id_sala = editarReserva.id_sala,
        status = editarReserva.status,
        feito_em = editarReserva.feito_em,
        entrada = editarReserva.entrada,
        saida = editarReserva.saida
    )

    del listaReservas[index] # Deleta o item do index indicado
    listaReservas.append(reservaEditada) 

    return listaReservas[-1]

# Informações específicas
@appReserva.patch("/reserva", status_code=status.HTTP_200_OK)
def editar(editarReserva: reservaEdicao):
    encontrado = False
    index = -1

    for item in listaReservas:
        index += 1
        if item.id == editarReserva.id:
            encontrado = True
            break
    if encontrado == False:
        raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
    reservaAntiga = listaReservas[index] # defino o que já existe em uma variável, pelo que entendi, por ser objeto a variável vira uma referência do item dentro da lista e não uma cópia como seria com um int ou str, então ao editar "a variável" eu estou editando na vdd o item da lista

    novosDados = editarReserva.model_dump(exclude_unset=True) # pego a entrada e excluo todos os itens nulos e só sobram atributos que vão ser modificados, e o id, no objeto

    for atributo, valor in novosDados.items(): # percorre todos os atributos que sobraram da entrada
        if atributo == "id":
            continue # pula o id para evitar processamento desnecessário

        setattr(reservaAntiga, atributo, valor) # Equiparado a objeto.nome = valor, mas como nesse caso o atributo do for é uma str então preciso entregar para essa função

    return listaReservas[index]

# Rota para exclusão de reservas ( talvez não faça sentido diretamente no negócio mas entendo ser ok de implementar pelo caso de um dia ser necessário e então já ter )
# Todas as reservas 
@appReserva.delete("/reserva", status_code=status.HTTP_204_NO_CONTENT)
def deletarTudo():
    listaReservas.clear()
    return

# Uma reserva específica
@appReserva.delete("/reserva/{id}", status_code=status.HTTP_204_NO_CONTENT)
def deletarUm(id: int):
    encontrado = False
    index = -1

    for item in listaReservas:
        index += 1
        if item.id == id:
            encontrado = True
            break
    if encontrado == False:
        raise HTTPException(status_code=404, detail="Reserva informada não encontrada") # Levanta erro caso a reserva pedida não existir
    
    del listaReservas[index]

    return # Terá mais complexidade quanto eu colocar o banco, pois terei que buscar nele as informações