import os
from concurrent import futures

from dotenv import load_dotenv
import grpc
import sounddevice as sd
import cv2

import protos.upload_pb2 as upload_pb2
import protos.upload_pb2_grpc as upload_pb2_grpc


load_dotenv()
PORT = os.getenv("PORT")

CHUNK = 4096
stream = sd.InputStream(
    samplerate=44100,
    channels=1,
    dtype="float32",
    blocksize=CHUNK
)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


class UploadServer(upload_pb2_grpc.UploadHandlerServicer):
    def __init__(self):
        pass

    def Upload(self, request_iterator, context):
        stream.start()
        try:
            for req in request_iterator:
                print(req.msg)

                while True:
                    ret, frame = cap.read()

                    if ret != 1:
                        continue

                    captureBuffer = frame
                    ret, buf = cv2.imencode('.jpg', captureBuffer)

                    indata, overflowed = stream.read(CHUNK)
                    yield upload_pb2.UploadReply(audio=indata.tobytes(), video=buf.tobytes())

        except Exception as e:
            print(e)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    upload_pb2_grpc.add_UploadHandlerServicer_to_server(UploadServer(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

cap.release()
