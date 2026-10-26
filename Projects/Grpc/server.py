"""Serveur gRPC (Laptop 1) : services sur les nombres premiers."""
import sys
from concurrent import futures

import grpc

import primes_pb2
import primes_pb2_grpc


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def factorize(n: int) -> list:
    """Factorisation en nombres premiers (ex. 100 -> [2, 2, 5, 5])."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


class PrimeService(primes_pb2_grpc.PrimeServiceServicer):
    # Appel normal : Requête/Réponse
    def IsPrime(self, request, context):
        n = request.n
        if n < 2:
            return primes_pb2.IsPrimeResponse(is_prime=False, factors=[])
        if is_prime(n):
            return primes_pb2.IsPrimeResponse(is_prime=True, factors=[])
        return primes_pb2.IsPrimeResponse(is_prime=False, factors=factorize(n))

    # Stream serveur -> client : envoie les nombres premiers un par un
    def FirstPrimes(self, request, context):
        count, candidate = 0, 2
        while count < request.n and context.is_active():
            if is_prime(candidate):
                yield primes_pb2.PrimeReply(prime=candidate)
                count += 1
            candidate += 1


def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    primes_pb2_grpc.add_PrimeServiceServicer_to_server(PrimeService(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")  # 0.0.0.0 : accessible depuis les autres machines
    server.start()
    print(f"Serveur démarré sur le port {port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 50051)
