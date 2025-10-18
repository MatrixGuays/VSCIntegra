#creando una lista ( se puede modificar)
Lista = ["A ver que se dice", 16, "¿entonces esto se puede?"]
print (Lista[0])

#Creando una tupla (No se puede modificar)
Quieta = ("decime algo lindo", 19, "Ahora no, no me digas nada lindo. Gay")
print (Quieta[0])

#Esto se puede hacer
Lista[0] = "Te cambie"
print (Lista[0])

#Esto no se puede hacer 
#Quieta[0] = "No te puedo cambiar "

#Creando un conjunto sett(No se puede  llamar a los elementos por su indice, no almacena tatos duplicados)

conjunto = {"Mi nombre", 19, "No se", True, 1.54}
print (conjunto)

#Creando un diccionario ( La estructura es key: Value y separamos con comas)
diccionario = {
    "Nombre" : "Nahuel",
    "Apellido" : "Ojeda",
    "Dato_Booleano": True,
    "Cuanto_Me_Mide" : 1.43
}
print (diccionario["Nombre"])
