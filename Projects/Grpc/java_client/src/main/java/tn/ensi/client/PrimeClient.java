package tn.ensi.client;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.StatusRuntimeException;
import tn.ensi.primes.IsPrimeResponse;
import tn.ensi.primes.NumberRequest;
import tn.ensi.primes.PrimeReply;
import tn.ensi.primes.PrimeServiceGrpc;

import java.util.Iterator;
import java.util.Scanner;
import java.util.StringJoiner;

/** Client gRPC Java (Laptop 2) avec menu. Usage : PrimeClient [hote] [port] */
public class PrimeClient {

    public static void main(String[] args) {
        String host = args.length > 0 ? args[0] : "localhost";
        int port = args.length > 1 ? Integer.parseInt(args[1]) : 50051;

        ManagedChannel channel = ManagedChannelBuilder.forAddress(host, port)
                .usePlaintext()
                .build();
        // Stub bloquant : convient à l'appel normal et au stream serveur -> client
        PrimeServiceGrpc.PrimeServiceBlockingStub stub = PrimeServiceGrpc.newBlockingStub(channel);

        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.println("\n=== Services nombres premiers ===");
            System.out.println("1. IsPrime(n)      - appel normal (requete/reponse)");
            System.out.println("2. FirstPrimes(n)  - stream serveur -> client");
            System.out.println("0. Quitter");
            System.out.print("Votre choix : ");
            String choix = sc.nextLine().trim();
            if (choix.equals("0")) break;
            if (!choix.equals("1") && !choix.equals("2")) {
                System.out.println("Choix invalide.");
                continue;
            }
            System.out.print("n = ");
            long n;
            try {
                n = Long.parseLong(sc.nextLine().trim());
            } catch (NumberFormatException e) {
                System.out.println("Veuillez saisir un entier.");
                continue;
            }

            try {
                NumberRequest req = NumberRequest.newBuilder().setN(n).build();
                if (choix.equals("1")) {
                    IsPrimeResponse r = stub.isPrime(req);
                    if (r.getIsPrime()) {
                        System.out.println(n + " est premier");
                    } else {
                        StringJoiner sj = new StringJoiner("*");
                        r.getFactorsList().forEach(f -> sj.add(String.valueOf(f)));
                        System.out.println(n + " Non premier"
                                + (r.getFactorsCount() > 0 ? " ; " + n + "=" + sj : ""));
                    }
                } else {
                    System.out.println("Les " + n + " premiers nombres premiers (stream) :");
                    Iterator<PrimeReply> it = stub.firstPrimes(req);
                    while (it.hasNext()) {
                        System.out.print(it.next().getPrime() + " ");
                    }
                    System.out.println();
                }
            } catch (StatusRuntimeException e) {
                System.out.println("Erreur gRPC : " + e.getStatus());
            }
        }
        channel.shutdown();
    }
}
