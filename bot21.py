import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telethon import TelegramClient, events, Button

API_ID = '0' #A insertar
API_HASH = '0' #A insertar
BOT_TOKEN = '0' #A insertar (usar botfather)

# Crear el cliente del bot
client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Configurar la autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\chatbot\\google credentials\\credentials.json' #Direccion local donde este tu credentials.json
, scope)
gs_client = gspread.authorize(creds)
sheet = gs_client.open("Chatbot Telegram").sheet1

# Función para guardar datos en Google Sheets
def save_to_google_sheets(data):
    sheet.append_row(data)

# Variables para almacenar el estado del usuario
user_states = {}

async def main():
    # Manejador de eventos para mensajes de texto
    @client.on(events.NewMessage)
    async def handle_message(event):
        try:
            print("Entrando en handle_message...")
            if event.message:
                message_text = event.message.text.lower()
                print(f"Mensaje recibido: {message_text}")

                user_id = event.sender_id
                
                if "hola" in message_text:
                    buttons = [
                        Button.inline("Solicitar Presupuesto", b"/solicitar"),
                        Button.inline("Soporte", b"/ayuda")
                    ]
                    response = (
                        "Hola, soy el bot de gestión de solicitudes de la multinacional Garbarino.\n"
                        "¿Qué te gustaría hacer?"
                    )
                    await event.respond(response, buttons=buttons)
                elif message_text == "/solicitar":
                    user_states[user_id] = {"step": 1, "data": {}}
                    response = "Por favor, proporciona tu nombre."
                    await event.respond(response)
                elif user_id in user_states:
                    step = user_states[user_id]["step"]
                    if step == 1:
                        user_states[user_id]["data"]["nombre"] = message_text
                        user_states[user_id]["step"] = 2
                        response = "Por favor, proporciona tu apellido."
                        await event.respond(response)
                    elif step == 2:
                        user_states[user_id]["data"]["apellido"] = message_text
                        user_states[user_id]["step"] = 3
                        response = "Por favor, proporciona tu número de documento."
                        await event.respond(response)
                    elif step == 3:
                        user_states[user_id]["data"]["numero_documento"] = message_text
                        user_states[user_id]["step"] = 4
                        response = "Por favor, proporciona tu número de teléfono."
                        await event.respond(response)
                    elif step == 4:
                        user_states[user_id]["data"]["numero_telefono"] = message_text
                        # Guardar la solicitud en Google Sheets
                        data = [
                            "/solicitar",
                            user_states[user_id]["data"]["nombre"],
                            user_states[user_id]["data"]["apellido"],
                            user_states[user_id]["data"]["numero_documento"],
                            user_states[user_id]["data"]["numero_telefono"]
                        ]
                        save_to_google_sheets(data)
                        response = "Gracias por tu solicitud. Hemos recibido tu información."
                        await event.respond(response)
                        del user_states[user_id]
                else:
                    response = "No entiendo ese comando. Por favor, envía 'hola' para ver la lista de comandos."
                    await event.respond(response)
            else:
                print("No se recibió un mensaje válido")
                
        except Exception as e:
            print(f"Error al manejar el mensaje: {e}")

    # Manejador de eventos para botones en línea
    @client.on(events.CallbackQuery)
    async def handle_callback(event):
        try:
            data = event.data.decode('utf-8')
            user_id = event.sender_id

            if data == "/solicitar":
                user_states[user_id] = {"step": 1, "data": {}}
                response = "Por favor, proporciona tu nombre."
                await event.respond(response)
            elif data == "/ayuda":
                response = (
                    "Hola, este es un bot de prueba, no cumple ninguna funcionalidad real y está a cargo de Estudillo Máximo.\n"
                    "El único comando disponible hasta ahora es /solicitar que guarda la información en Google Sheets con link:\n"
                    "https://docs.google.com/spreadsheets/d/10OBVSZRNhw8evri1t8ZUs6MCO3KI6JbP1ASzXGAI4sk/edit?usp=sharing"
                )
                await event.respond(response)
            else:
                response = "No entiendo ese comando. Por favor, envía 'hola' para ver la lista de comandos."
                await event.respond(response)
        except Exception as e:
            print(f"Error al manejar el callback: {e}")


    # Iniciar el cliente
    print("Bot iniciado. Esperando mensajes...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Asegúrate de que el bucle de eventos de asyncio se establece correctamente
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
