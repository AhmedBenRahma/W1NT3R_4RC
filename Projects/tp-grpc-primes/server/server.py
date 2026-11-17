
from concurrent import futures
import grpc

import prime_pb2 as pb2
import prime_pb2_grpc as pb2_grpc


def is_prime(n):
    if n < 2:
        return False

    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1

    return True


def prime_factors(n):
    factors = []
    i = 2

    while n > 1 and i <= n:
        while n % i == 0:
            factors.append(i)
            n //= i
        i += 1

    if n > 1:
        factors.append(n)

    return factors


def first_primes(n):
    primes = []
    i = 2

    while len(primes) < n:
        if is_prime(i):
            primes.append(i)
        i += 1

    return primes


class FirstPrimeService(pb2_grpc.FirstPrimeServiceServicer):
    def FirstPrime(self, request, context):
        response = pb2.NPremiers()
        response.range.extend(first_primes(request.n))
        return response


class FirstPrimeStreamService(pb2_grpc.FirstPrimeStreamServiceServicer):
    def FirstPrimeStream(self, request, context):
        for prime in first_primes(request.n):
            yield pb2.NPremiersStream(range=prime)


class IsPrimeService(pb2_grpc.IsPrimeServiceServicer):
    def IsPrime(self, request, context):
        n = request.n
        prime = is_prime(n)

        response = pb2.output(b=prime)

        if not prime and n > 1:
            response.fact.extend(prime_factors(n))

        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    pb2_grpc.add_FirstPrimeServiceServicer_to_server(
        FirstPrimeService(), server
    )
    pb2_grpc.add_FirstPrimeStreamServiceServicer_to_server(
        FirstPrimeStreamService(), server
    )
    pb2_grpc.add_IsPrimeServiceServicer_to_server(
        IsPrimeService(), server
    )

    server.add_insecure_port("[::]:50051")
    server.start()

    print("gRPC server listening on port 50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
