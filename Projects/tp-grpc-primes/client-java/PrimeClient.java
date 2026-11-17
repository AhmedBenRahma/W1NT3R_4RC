package tp_grpc.prime_client;


import java.util.Iterator;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;

public class PrimeClient {

    public static void main(String[] args) throws InterruptedException {

        ManagedChannel channel = ManagedChannelBuilder
                .forAddress("10.18.54.116", 50051)
                .usePlaintext()
                .build();

        FirstPrimeServiceGrpc.FirstPrimeServiceBlockingStub firstStub =
                FirstPrimeServiceGrpc.newBlockingStub(channel);

        FirstPrimeStreamServiceGrpc.FirstPrimeStreamServiceBlockingStub streamStub =
                FirstPrimeStreamServiceGrpc.newBlockingStub(channel);

        IsPrimeServiceGrpc.IsPrimeServiceBlockingStub isPrimeStub =
                IsPrimeServiceGrpc.newBlockingStub(channel);

        Scanner scanner = new Scanner(System.in);
        boolean running = true;

        try {
            while (running) {
                System.out.println("\n===== PRIME NUMBER CLIENT =====");
                System.out.println("1. Check if a number is prime");
                System.out.println("2. Get the first n primes (unary)");
                System.out.println("3. Get the first n primes (streaming)");
                System.out.println("0. Exit");
                System.out.print("Choose an option: ");

                if (!scanner.hasNextInt()) {
                    System.out.println("Please enter a valid menu option.");
                    scanner.next();
                    continue;
                }

                int choice = scanner.nextInt();

                switch (choice) {

                    case 1: {
                        System.out.print("Enter an integer: ");
                        long n = scanner.nextLong();

                        GetNumber request = GetNumber.newBuilder()
                                .setN(n)
                                .build();

                        output response = isPrimeStub.isPrime(request);

                        if (response.getB()) {
                            System.out.println(n + " is prime.");
                        } else {
                            System.out.println(n + " is not prime.");

                            List<Long> factors = response.getFactList();

                            if (!factors.isEmpty()) {
                                System.out.println("Prime factors: " + factors);
                            } else {
                                System.out.println(
                                        "No prime factorization returned for this input.");
                            }
                        }
                        break;
                    }

                    case 2: {
                        System.out.print("How many primes? ");
                        long n = scanner.nextLong();

                        if (n < 0 || n > 10000) {
                            System.out.println("Enter a count between 0 and 10000.");
                            break;
                        }

                        GetNumber request = GetNumber.newBuilder()
                                .setN(n)
                                .build();

                        NPremiers response = firstStub.firstPrime(request);

                        System.out.println("First " + n + " primes:");
                        System.out.println(response.getRangeList());
                        break;
                    }

                    case 3: {
                        System.out.print("How many primes to stream? ");
                        long n = scanner.nextLong();

                        if (n < 0 || n > 10000) {
                            System.out.println("Enter a count between 0 and 10000.");
                            break;
                        }

                        GetNumber request = GetNumber.newBuilder()
                                .setN(n)
                                .build();

                        Iterator<NPremiersStream> responses =
                                streamStub.firstPrimeStream(request);

                        System.out.println("Streaming primes:");

                        while (responses.hasNext()) {
                            NPremiersStream response = responses.next();
                            System.out.println(response.getRange());
                        }
                        break;
                    }

                    case 0:
                        running = false;
                        break;

                    default:
                        System.out.println("Unknown option.");
                }
            }

        } catch (StatusRuntimeException e) {
            System.err.println("gRPC request failed: " + e.getStatus());
        } finally {
            scanner.close();
            channel.shutdown();

            if (!channel.awaitTermination(5, TimeUnit.SECONDS)) {
                channel.shutdownNow();
            }
        }
    }
}
