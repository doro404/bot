#!/usr/bin/env python3
import telebot
from telebot import types
import mercadopago
import datetime
import time
import base64

import string
import random
import pymysql
import os
from PIL import Image
from io import BytesIO


def generate_token(length=15):
    characters = string.ascii_uppercase + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token



token_bot = "7082852144:AAHl6NOGCgrcNzejNEYN33k7fzTE5ydstGw"

access_token = '7082852144:AAHl6NOGCgrcNzejNEYN33k7fzTE5ydstGw'

ids = [6423539592]

bot = telebot.TeleBot(token_bot)

user_state = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    itembtn1 = types.InlineKeyboardButton(text='Comprar Mensal', callback_data='opcao1')
    itembtn2 = types.InlineKeyboardButton(text='Compar Anual', callback_data='opcao2')
    itembtn3 = types.InlineKeyboardButton(text='Renovar Mensal', callback_data='opcao3')
    itembtn4 = types.InlineKeyboardButton(text='Renovar Anual', callback_data='opcao4')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)

    photo_url = "https://cdn.discordapp.com/attachments/1074825624172118147/1128906077174505592/recurso.jpg"
    caption = "👋 Olá! Bem-vindo ao bot Atlas. Aqui estão algumas opções disponíveis:\n\n" \
          "💳 Comprar Plano Mensal = R$ 30,00\n" \
          "💳 Comprar Plano Anual = R$ 150,00\n" \
          "🔄 Renovar Plano Mensal = R$ 30,00\n" \
          "🔄 Renovar Plano Anual = R$ 150,00\n\n" \
          "Escolha uma opção para prosseguir:"


    bot.send_photo(message.chat.id, photo=photo_url, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'opcao1':
        bot.send_message(call.message.chat.id, 'Envie o Domínio do Painel, Exemplo: painel.seudominio.com.br.')
        user_state[call.message.chat.id] = {'opcao': 'opcao1', 'step': 'waiting_domain'}
    elif call.data == 'opcao2':
        bot.send_message(call.message.chat.id, 'Envie o Domínio do Painel, Exemplo: painel.seudominio.com.br.')
        user_state[call.message.chat.id] = {'opcao': 'opcao2', 'step': 'waiting_domain'}
    elif call.data == 'opcao3':
        bot.send_message(call.message.chat.id, 'Envie o Domínio do Painel, Exemplo: painel.seudominio.com.br.')
        user_state[call.message.chat.id] = {'opcao': 'opcao3', 'step': 'waiting_domain'}
    elif call.data == 'opcao4':
        bot.send_message(call.message.chat.id, 'Envie o Domínio do Painel, Exemplo: painel.seudominio.com.br.')
        user_state[call.message.chat.id] = {'opcao': 'opcao4', 'step': 'waiting_domain'}
    elif call.data == 'confirm':
        domain_info = user_state.get(call.message.chat.id)
        if domain_info and domain_info.get('step') == 'waiting_confirmation':
            domain = domain_info.get('domain')
            opcao = domain_info.get('opcao')
            process_payment(call.message.chat.id, domain, opcao)
        else:
            bot.answer_callback_query(call.id, 'Nenhum domínio confirmado.')
    elif call.data == 'cancel':
        bot.answer_callback_query(call.id, 'Operação cancelada.')
        user_state[call.message.chat.id] = ''
        start(call.message)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get('step') == 'waiting_domain')
def process_domain(message):
    domain = message.text.strip()  # Remover espaços extras antes e depois do domínio
    domain = domain.replace("'", "")
    domain = domain.replace('"', '')
    domain = domain.replace(';', '')
    domain = domain.replace('=', '')
    domain = domain.replace('(', '')
    domain = domain.replace(')', '')
    domain = domain.replace('!', '')
    domain = domain.replace('#', '')
    domain = domain.replace('$', '')
    domain = domain.replace('%', '')
    domain = domain.replace('&', '')
    domain = domain.replace('*', '')        

    # Verificar se o domínio é válido
    if not domain or domain.startswith(('http://', 'https://')):
        bot.send_message(message.chat.id, "O domínio não é válido. Por favor, insira um domínio válido.")
        return
 
    user_state[message.chat.id]['domain'] = domain  # Adicionar o domínio ao dicionário user_state
    user_state[message.chat.id]['step'] = 'waiting_confirmation'
    
    confirmation_markup = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(text='Confirmar', callback_data='confirm')
    cancel_button = types.InlineKeyboardButton(text='Cancelar', callback_data='cancel')
    confirmation_markup.add(confirm_button, cancel_button)
    opcao = user_state[message.chat.id].get('opcao')
    if opcao == 'opcao1':
        valor = '30.00'
        plano = 'Comprar Plano Mensal'
    elif opcao == 'opcao2':
        valor = '150.00'
        plano = 'Comprar Plano Anual'
    elif opcao == 'opcao3':
        valor = '30.00'
        plano = 'Renovar Plano Mensal'
    elif opcao == 'opcao4':
        valor = '150.00'
        plano = 'Renovar Plano Anual'
    bot.send_message(message.chat.id, f'Você digitou o domínio: {domain}.\n Você esta prestes a {plano} no valor de R$ {valor}.\n\n' f'Para confirmar, clique no botão abaixo:', reply_markup=confirmation_markup)

@bot.message_handler(func=lambda message: user_state.get(message.chat.id, {}).get('step') == 'waiting_confirmation')
def process_confirmation(message):
    confirmation = message.text.strip().lower()

    if confirmation == 'confirmar':
        domain_info = user_state.get(message.chat.id)
        domain = domain_info.get('domain')
        opcao = domain_info.get('opcao')
        process_payment(message.chat.id, domain, opcao)
    else:
        bot.send_message(message.chat.id, 'Operação cancelada.')
        user_state[message.chat.id] = ''
        start(message)

def process_payment(chat_id, domain, opcao):

    if opcao == 'opcao1':
        valor = '30.00'
    elif opcao == 'opcao2':
        valor = '150.00'
    elif opcao == 'opcao3':
        valor = '30.00'
    elif opcao == 'opcao4':
        valor = '150.00'

    sdk = mercadopago.SDK(access_token)
    expire = datetime.datetime.now() + datetime.timedelta(minutes=10)
    date_of_expiration = expire.strftime("%Y-%m-%dT%H:%M:%S.000-03:00")



    payment_data = {
        "transaction_amount": float(valor),
        "description": "Plano Atlas",
        "payment_method_id": 'pix',
        "installments": 1,
        "date_of_expiration": date_of_expiration,
        "payer": {
            "email": 'atlasdesenvolvimentovpn@gmail.com'
        }
    }
    result = sdk.payment().create(payment_data)
    if result["status"] == 201:
        pix_copia_cola = result["response"]["point_of_interaction"]["transaction_data"]["qr_code"]
        qr_code_base64 = result["response"]["point_of_interaction"]["transaction_data"]["qr_code_base64"]
        image_data = base64.b64decode(qr_code_base64)
        image = Image.open(BytesIO(image_data))
        image_path = "qr_code" + str(chat_id) + ".png"
        image.save(image_path)
        with open(image_path, 'rb') as photo:
            bot.send_photo(
                chat_id,
                photo,
                caption=f'Para efetuar o pagamento, copie e cole o código abaixo no seu aplicativo do banco:\n\n'
                f"<code>{pix_copia_cola}</code>",
                parse_mode='HTML'
            )

        os.remove(image_path)
        # Store the payment_id and other relevant information in the user_state
        user_state[chat_id] = {'step': 'waiting_payment', 'payment_id': result["response"]["id"]}
        check_payment_status(chat_id, result["response"]["id"], time.time(), domain, opcao=opcao)

    else:
        bot.send_message(chat_id, 'Não foi possível gerar o QR Code. Por favor, tente novamente mais tarde.')

def string_to_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%d/%m/%Y")    

# ... (código anterior)

@bot.message_handler(commands=['cancelar'])
def cancel_payment(message):
    if user_state != {}:
        chat_id = message.chat.id
        payment_info = user_state.get(chat_id)
        if payment_info and payment_info.get('step') == 'waiting_payment':
            payment_id = payment_info.get('payment_id')
            if payment_id:
                sdk = mercadopago.SDK(access_token)
                result = sdk.payment().get(payment_id)
                if result["status"] == 200:
                    payment_status = result["response"]["status"]
                    if payment_status == "approved":
                        bot.send_message(chat_id, "O pagamento já foi aprovado e não pode ser cancelado.")
                        return
                    result = sdk.payment().update(payment_id, {"status": "cancelled"})
                    if result["status"] == 200:
                        bot.send_message(chat_id, "Pagamento cancelado com sucesso.")
                        user_state[chat_id] = ''
                        start(message)
                    else:
                        bot.send_message(chat_id, "Erro ao cancelar o pagamento. Por favor, tente novamente mais tarde.")
                else:
                    bot.send_message(chat_id, "Erro ao verificar o status do pagamento. Por favor, tente novamente mais tarde.")
            else:
                bot.send_message(chat_id, "Não foi possível encontrar o ID do pagamento. Por favor, tente novamente.")
        else:
            #bot.send_message(chat_id, "Não há pagamento em processo para ser cancelado.")
            return

    
def save_payment_data(domain, tipo_plano, valor):
    with open('pagamentos_aprovados.txt', 'a') as arquivo:
        arquivo.write(f'Dominio: {domain}, Plano: {tipo_plano}, Valor: {valor}\n')

def calculate_total_earnings():
    total_earnings = 0.0
    with open('pagamentos_aprovados.txt', 'r') as arquivo:
        for linha in arquivo:
            # Supondo que o arquivo está no formato "Domain: dominio, Opcao: opcao, Valor: valor"
            if 'Valor' in linha:
                valor_str = linha.split('Valor: ')[1].strip()
                valor = float(valor_str)
                total_earnings += valor
    return total_earnings
      
@bot.message_handler(commands=['total'])
def show_total_earnings(message):
    # Verificar se o ID do chat é igual ao ID desejado (2017803306)
    if message.chat.id == ids[0] or message.chat.id == ids[1]:
        total_ganho = calculate_total_earnings()
        bot.send_message(message.chat.id, f'O total de Vendas é: R$ {total_ganho:.2f}')

@bot.message_handler(commands=['logs'])
def send_logs(message):
    # Verificar se o ID do chat é igual ao ID desejado (2017803306)
    if message.chat.id == ids[0] or message.chat.id == ids[1]:
        try:
            with open('pagamentos_aprovados.txt', 'r') as arquivo:
                logs = arquivo.read()
            if not logs.strip():  # Verificar se a variável logs está vazia
                bot.send_message(message.chat.id, 'O arquivo de logs está vazio.')
            else:
                bot.send_message(message.chat.id, logs)
        except FileNotFoundError:
            bot.send_message(message.chat.id, 'O arquivo de logs não foi encontrado.')



# Comando /zerar
@bot.message_handler(commands=['zerar'])
def zerar_comando(message):
    chat_id_permitido = 2017803306
    if message.chat.id == chat_id_permitido:
        with open("pagamentos_aprovados.txt", "w") as arquivo:
            arquivo.write("")
        bot.send_message(message.chat.id, "Arquivo de pagamentos aprovados zerado com sucesso.")



def check_payment_status(chat_id, payment_id, start_time, domain=None, opcao=None):
    current_time = time.time()
    elapsed_time = current_time - start_time
    time_remaining = max(10 * 60 - elapsed_time, 0)

    if time_remaining == 0:
        bot.send_message(chat_id, "Tempo esgotado para verificar o status do pagamento.")
        return

    sdk = mercadopago.SDK(access_token)
    result = sdk.payment().get(payment_id)
    if result["status"] == 200:
        payment_status = result["response"]["status"]
        if payment_status == "pending":
            minutes_remaining = int(time_remaining // 60)
            seconds_remaining = int(time_remaining % 60)
            remaining_message = f"⏳ Pagamento em processamento. Tempo Restante: {minutes_remaining:02d}:{seconds_remaining:02d}\n❌ Para cancelar o pagamento, digite /cancelar"
            message_id = None
            if message_id is None:
                message = bot.send_message(chat_id, remaining_message)
                message_id = message.message_id

            while time_remaining > 0:
                time.sleep(2)  # Tempo de atualização
                current_time = time.time()
                elapsed_time = current_time - start_time
                time_remaining = max(10 * 60 - elapsed_time, 0)
                minutes_remaining = int(time_remaining // 60)
                seconds_remaining = int(time_remaining % 60)
                new_remaining_message = f"⏳ Pagamento em processamento. Tempo Restante: {minutes_remaining:02d}:{seconds_remaining:02d}\n❌ Para cancelar o pagamento, digite /cancelar"

                if new_remaining_message != remaining_message:
                    bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_remaining_message)
                    remaining_message = new_remaining_message

                sdk = mercadopago.SDK(access_token)
                result = sdk.payment().get(payment_id)
                payment_status = result["response"]["status"]
                if payment_status == "approved":
                    if opcao == 'opcao1':
                        tipo_plano = 'Compra Mensal'
                    elif opcao == 'opcao2':
                        tipo_plano = 'Compra Anual'
                    elif opcao == 'opcao3':
                        tipo_plano = 'Renovação Mensal'
                    elif opcao == 'opcao4':
                        tipo_plano = 'Renovação Anual'
                    

                    bot.send_message(chat_id, "Pagamento aprovado! Obrigado pela sua compra.")
                    
                    token = generate_token()

                    host = ""
                    dbname = ""
                    dbuser = ""
                    dbpass = ""
                    port = 3306
                    conn = pymysql.connect(host=host, port=port, user=dbuser, passwd=dbpass, db=dbname)

                    vencimento = datetime.datetime.now() + datetime.timedelta(days=30)
                    data = vencimento.strftime("%d/%m/%Y")

                    vencimento_anual = datetime.datetime.now() + datetime.timedelta(days=365)
                    vencimento_anual = vencimento_anual.strftime("%d/%m/%Y")

                    if (opcao == 'opcao1'):
                        cur = conn.cursor()
                        cur.execute("INSERT INTO `atlaspainel`.`tokens` (`dominio`, `token`, `vencimento`, `dono`, `contato`) VALUES ('"+domain+"', '"+token+"', '"+str(data)+"', '0', '0');")
                        conn.commit()
                        conn.close()
                        save_payment_data(domain, tipo_plano, result["response"]["transaction_amount"])
                        bot.send_message(chat_id, f'Suas Credenciais do painel são:\n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Para resgatar o token, acesse o link: https://atlaspainel.shop \n\n' f'Guia de instalação: https://docs.atlaspainel.com.br/ \n Caso tenha algum problema contate https://wa.link/699q2j')
                        bot.send_message(ids[0], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f}')
                        bot.send_message(ids[1], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f}')
                    elif (opcao == 'opcao2'):
                        cur = conn.cursor()
                        cur.execute("INSERT INTO `atlaspainel`.`tokens` (`dominio`, `token`, `vencimento`, `dono`, `contato`) VALUES ('"+domain+"', '"+token+"', '"+str(vencimento_anual)+"', '0', '0');")
                        conn.commit()
                        conn.close()
                        save_payment_data(domain, tipo_plano, result["response"]["transaction_amount"])
                        bot.send_message(chat_id, f'Suas Credenciais do painel são:\n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(vencimento_anual)+'\n\n' f'Para resgatar o token, acesse o link: https://atlaspainel.shop \n\n' f'Guia de instalação: https://docs.atlaspainel.com.br/ \n Caso tenha algum problema contate https://wa.link/699q2j')  
                        bot.send_message(ids[0], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                        bot.send_message(ids[1], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                    elif (opcao == 'opcao3'):
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM `atlaspainel`.`tokens` WHERE `dominio` = '"+domain+"'")
                        row = cur.fetchone()
                        if row is not None:
                            data_vencimento = row[4]  # Assumindo que a coluna de vencimento é a quinta coluna (índice 4) na tabela
                            data_vencimento = string_to_datetime(data_vencimento)  # Convertendo a string para datetime
                            periodo = datetime.timedelta(days=30)  # 30 dias para opção 3 (pode ser alterado conforme necessário)

                            nova_data_vencimento = data_vencimento + periodo

                            nova_data_vencimento = nova_data_vencimento.strftime("%d/%m/%Y")
                            cur.execute("UPDATE `atlaspainel`.`tokens` SET `vencimento` = '"+str(nova_data_vencimento)+"' WHERE `dominio` = '"+domain+"';")
                            conn.commit()
                            conn.close()
                            save_payment_data(domain, tipo_plano, result["response"]["transaction_amount"])
                            bot.send_message(chat_id, f'Renovado com sucesso, sua nova data de vencimento é: {nova_data_vencimento}')
                            bot.send_message(ids[0], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                            bot.send_message(ids[1], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                        else:
                            bot.send_message(chat_id, f'Seu token não foi encontrado, Provavelmente já foi deletado por esta vencido ou não existe \n\n'f'Estamos estornando o valor pago, caso tenha duvidas entre em contato com o suporte. https://wa.link/699q2j \n\n'f'Caso você queira renovar seu token, basta comprar um novo token mais você terar que mudar seu token na hospedagem.')
                            bot.send_message(ids[0], f'Token não encontrado: \n\n' f'Domínio: {domain}\n' f'Plano: {tipo_plano}\n\n' f'Valor Estornado: R$ {result["response"]["transaction_amount"]:.2f} \n Username: @{message.chat.username}')
                            bot.send_message(ids[1], f'Token não encontrado: \n\n' f'Domínio: {domain}\n' f'Plano: {tipo_plano}\n\n' f'Valor Estornado: R$ {result["response"]["transaction_amount"]:.2f} \n Username: @{message.chat.username}')
                            sdk = mercadopago.SDK(access_token)
                            
                            refund_object = {
                            'amount': result["response"]["transaction_amount"],
                            }

                            request_options = mercadopago.config.RequestOptions()
                            request_options.custom_headers = {
                            'content-type': 'application/json',
                            'X-Render-In-Process-Refunds': 'true'
                            }

                            result_estorn = sdk.refund().create(result["response"]["id"], refund_object, request_options)
                            if result_estorn["status"] == 201:
                                bot.send_message(chat_id, "Pagamento estornado com sucesso. Para iniciar uma nova compra, digite /start")
                            


                    elif (opcao == 'opcao4'):
                        cur = conn.cursor()
                        cur.execute("SELECT * FROM `atlaspainel`.`tokens` WHERE `dominio` = '"+domain+"'")
                        row = cur.fetchone()
                        if row is not None:
                            data_vencimento = row[4]
                            data_vencimento = string_to_datetime(data_vencimento)
                            periodo = datetime.timedelta(days=365)
                            nova_data_vencimento = data_vencimento + periodo
                            nova_data_vencimento = nova_data_vencimento.strftime("%d/%m/%Y")
                            cur.execute("UPDATE `atlaspainel`.`tokens` SET `vencimento` = '"+str(nova_data_vencimento)+"' WHERE `dominio` = '"+domain+"';")
                            conn.commit()
                            conn.close()
                            save_payment_data(domain, tipo_plano, result["response"]["transaction_amount"])
                            bot.send_message(chat_id, f'Renovado com sucesso, sua nova data de vencimento é: {nova_data_vencimento}')
                            bot.send_message(ids[0], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                            bot.send_message(ids[1], f'Nova Venda: \n\n' f'Domínio: {domain}\n' f'Token: {token}\n\n' f'Vencimento: '+str(data)+'\n\n' f'Plano: {tipo_plano}\n\n' f'Valor: R$ {result["response"]["transaction_amount"]:.2f} Username: @{message.chat.username}')
                        else:
                            bot.send_message(chat_id, f'Seu token não foi encontrado, Provavelmente já foi deletado por esta vencido ou não existe \n\n'f'Estamos estornando o valor pago, caso tenha duvidas entre em contato com o suporte. https://wa.link/699q2j \n\n'f'Caso você queira renovar seu token, basta comprar um novo token mais você terar que mudar seu token na hospedagem.')
                            bot.send_message(ids[0], f'Token não encontrado: \n\n' f'Domínio: {domain}\n' f'Plano: {tipo_plano}\n\n' f'Valor Estornado: R$ {result["response"]["transaction_amount"]:.2f} \n Username: @{message.chat.username}')

                            bot.send_message(ids[1], f'Token não encontrado: \n\n' f'Domínio: {domain}\n' f'Plano: {tipo_plano}\n\n' f'Valor Estornado: R$ {result["response"]["transaction_amount"]:.2f} \n Username: @{message.chat.username}')
                            sdk = mercadopago.SDK(access_token)
                            
                            refund_object = {
                            'amount': result["response"]["transaction_amount"],
                            }

                            request_options = mercadopago.config.RequestOptions()
                            request_options.custom_headers = {
                            'content-type': 'application/json',
                            'X-Render-In-Process-Refunds': 'true'
                            }

                            result_estorn = sdk.refund().create(result["response"]["id"], refund_object, request_options)
                            if result_estorn["status"] == 201:
                                bot.send_message(chat_id, "Pagamento estornado com sucesso. Para iniciar uma nova compra, digite /start")
                    break
                elif payment_status == "cancelled":
                    #bot.send_message(chat_id, "Pagamento cancelado.")
                    return
            
            if new_remaining_message != remaining_message:
                bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=new_remaining_message)

        elif payment_status == "cancelled":
            ##bot.send_message(chat_id, "Pagamento cancelado.")
            return
        
        else:
            bot.send_message(chat_id, "Pagamento não aprovado. Por favor, entre em contato com o suporte.")
    else:
        bot.send_message(chat_id, "Erro ao verificar o status do pagamento. Por favor, tente novamente mais tarde.")


    
bot.polling()