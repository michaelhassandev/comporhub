import os
from datetime import datetime, timedelta
from twilio.rest import Client
from models import Singer

# Configure as credenciais do Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")


def enviar_sms_exclusividade(to_phone_number, nome_cantor, nome_composicao, dias_restantes, data_expiracao):
    """
    Envia um SMS para o compositor informando sobre a exclusividade prestes a expirar.
    
    Args:
        to_phone_number (str): Número de telefone do compositor
        nome_cantor (str): Nome do cantor
        nome_composicao (str): Nome da composição
        dias_restantes (int): Dias restantes até o fim da exclusividade
        data_expiracao (date): Data em que a exclusividade expira
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("Credenciais do Twilio não configuradas. Não é possível enviar SMS.")
        return False
    
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Formatar a mensagem
    mensagem = (
        f"[Hub do Compositor] Exclusividade prestes a vencer! "
        f"A exclusividade do cantor {nome_cantor} para a composição '{nome_composicao}' "
        f"vence em {dias_restantes} dias ({data_expiracao.strftime('%d/%m/%Y')}). "
        f"Acesse seu painel para gerenciar."
    )
    
    try:
        # Enviando o SMS
        message = client.messages.create(
            body=mensagem,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        print(f"SMS enviado com SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Erro ao enviar SMS: {e}")
        return False


def verificar_exclusividades_vencendo(app, dias_aviso=7):
    """
    Verifica todas as exclusividades que estão prestes a vencer e envia SMS
    para os compositores.
    
    Args:
        app: Aplicação Flask
        dias_aviso (int): Número de dias antes do vencimento para enviar o aviso
    """
    with app.app_context():
        hoje = datetime.utcnow().date()
        data_limite = hoje + timedelta(days=dias_aviso)
        
        # Buscar exclusividades que vencem em breve
        cantores = Singer.query.filter(
            Singer.exclusive_until <= data_limite,
            Singer.exclusive_until >= hoje
        ).all()
        
        for cantor in cantores:
            # Verificar se o compositor tem número de telefone cadastrado
            if cantor.owner.phone:
                dias_restantes = (cantor.exclusive_until - hoje).days
                
                enviar_sms_exclusividade(
                    to_phone_number=cantor.owner.phone,
                    nome_cantor=cantor.name,
                    nome_composicao=cantor.composition.title,
                    dias_restantes=dias_restantes,
                    data_expiracao=cantor.exclusive_until
                )
