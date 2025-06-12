import grpc
import image_pb2, image_pb2_grpc
import sys

SERVER_ADDRESS = "13.220.235.189:50051"
IMAGE_PATH = "TORTA.jpg"

if len(sys.argv) >= 2:
    IMAGE_PATH = sys.argv[1]
if len(sys.argv) >= 3:
    SERVER_ADDRESS = sys.argv[2]

with open(IMAGE_PATH, 'rb') as img_file:
    image_bytes = img_file.read()
filename = IMAGE_PATH.split('/')[-1]

channel = grpc.insecure_channel(SERVER_ADDRESS)
stub = image_pb2_grpc.ImageServiceStub(channel)

print(f"Enviando imagem '{filename}' para {SERVER_ADDRESS}...")
request = image_pb2.ImageRequest(filename=filename, image_data=image_bytes)
response = stub.SendImage(request)
if response.success:
    print("✔ Sucesso: " + response.message)
    print(f"Imagem enviada com sucesso. Verifique o bucket S3 ({filename} -> conversão concluída).")
else:
    print("✘ Falha: " + response.message)
