from concurrent import futures

import grpc
import pika

import image_pb2
import image_pb2_grpc


rabbit_conn = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = rabbit_conn.channel()
channel.queue_declare(queue='images', durable=False)


class ImageServiceServicer(image_pb2_grpc.ImageServiceServicer):
    def SendImage(self, request, context):

        filename = request.filename
        image_data = request.image_data
        try:

            props = pika.BasicProperties(headers={'filename': filename})
            channel.basic_publish(exchange='',
                                  routing_key='images',
                                  body=image_data,
                                  properties=props)
            print(f"[Produtor] Imagem '{filename}' publicada na fila para "
                  f"processamento.")

            response_msg = (f"Imagem {filename} recebida, processamento "
                            f"iniciado.")
            return image_pb2.ImageResponse(success=True, message=response_msg)
        except Exception as e:
            print(f"[Produtor] Erro ao publicar mensagem RabbitMQ: {e}")

            return image_pb2.ImageResponse(success=False, message="Erro no "
                                                                  "servidor ao"
                                                                  " enfileirar"
                                                                  " imagem.")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    image_pb2_grpc.add_ImageServiceServicer_to_server(ImageServiceServicer(),
                                                      server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor gRPC iniciado na porta 50051...")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
