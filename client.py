import os

from dotenv import load_dotenv
import numpy as np
import grpc
import sounddevice as sd
import cv2

import protos.upload_pb2 as upload_pb2
import protos.upload_pb2_grpc as upload_pb2_grpc

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

CHUNK = 4096
stream = sd.OutputStream(
    samplerate=44100,
    channels=1,
    dtype="float32",
    blocksize=CHUNK
)


def run():
    with grpc.insecure_channel(f"{HOST}:{PORT}") as channel:
        stream.start()
        stub = upload_pb2_grpc.UploadHandlerStub(channel)
        try:
           while True:
                message = []
                message.append(upload_pb2.UploadRequest(msg="request"))
                responses = stub.Upload(iter(message))

                for res in responses:
                    audio_buf = np.frombuffer(res.audio, dtype=np.float32)
                    stream.write(audio_buf)

                    dBuf = np.frombuffer(res.video, dtype=np.uint8)
                    dst = cv2.imdecode(dBuf, cv2.IMREAD_COLOR)
                    cv2.imshow("Capture Image", dst)

                    k = cv2.waitKey(1)
                    if k == 27:
                        break
    
        except grpc.RpcError as e:
            print(e)


if __name__ == "__main__":
    run()

