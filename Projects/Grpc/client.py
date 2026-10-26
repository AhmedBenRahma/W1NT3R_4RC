"""Client gRPC Python avec menu. Usage : python client.py [hote:port]"""
import sys

import grpc

import primes_pb2
import primes_pb2_grpc


def menu(stub):
    while True:
        print("\n=== Services nombres premiers ===")
        print("1. IsPrime(n)      - appel normal (requête/réponse)")
        print("2. FirstPrimes(n)  - stream serveur -> client")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()

        if choix == "0":
            break
        if choix not in ("1", "2"):
            print("Choix invalide.")
            continue
        try:
            n = int(input("n = ").strip())
        except ValueError:
            print("Veuillez saisir un entier.")
            continue

        try:
            if choix == "1":
                r = stub.IsPrime(primes_pb2.NumberRequest(n=n))
                if r.is_prime:
                    print(f"{n} est premier")
                else:
                    f = "*".join(map(str, r.factors))
                    print(f"{n} Non premier" + (f" ; {n}={f}" if r.factors else ""))
            else:
                print(f"Les {n} premiers nombres premiers (reçus en stream) :")
                for reply in stub.FirstPrimes(primes_pb2.NumberRequest(n=n)):
                    print(reply.prime, end=" ", flush=True)
                print()
        except grpc.RpcError as e:
            print(f"Erreur gRPC : {e.code()} - {e.details()}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    with grpc.insecure_channel(target) as channel:
        menu(primes_pb2_grpc.PrimeServiceStub(channel))
