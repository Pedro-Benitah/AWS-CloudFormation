import os, io
import pika
from PIL import Image
import boto3

rabbit_host = os.getenv('RABBIT_HOST', 'localhost')
bucket_name = os.getenv('BUCKET_NAME')
if not bucket_name:
    raise Exception("Bucket S3 não especificado. Verifique variáveis de ambiente.")

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
channel = connection.channel()
channel.queue_declare(queue='images', durable=False)
print(f"[Worker] Conectado ao RabbitMQ em {rabbit_host}, aguardando mensagens...")

s3_client = boto3.client('s3')

def process_image(ch, method, properties, body):
    """Callback chamado ao receber uma mensagem da fila."""
    try:
        filename = properties.headers.get('filename', 'imagem_desconhecida')
        print(f"[Worker] Processando imagem '{filename}'...")
        image = Image.open(io.BytesIO(body))
        gray_image = image.convert('L')
        base_name, ext = os.path.splitext(filename)
        output_name = f"{base_name}_gray{ext}"
        img_format = 'JPEG'
        if ext.lower() in ['.png']:
            img_format = 'PNG'
        buffer = io.BytesIO()
        gray_image.save(buffer, format=img_format)
        buffer.seek(0)
        s3_client.put_object(Bucket=bucket_name, Key=output_name, Body=buffer.getvalue())
        print(f"[Worker] Imagem processada enviada para S3: Bucket={bucket_name}, Key={output_name}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"[Worker] Erro no processamento da imagem: {e}")

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='images', on_message_callback=process_image, auto_ack=False)
channel.start_consuming()
