# TP gRPC : nombres premiers

## Fichiers
- `primes.proto` : contrat (messages + service)
- `server.py` : serveur Python (Laptop 1)
- `client.py` : client Python avec menu (test local)
- `java_client/` : client Java avec menu (Laptop 2)

## 1. Python (serveur et client de test)
```
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. primes.proto
python server.py            # écoute sur 0.0.0.0:50051
python client.py localhost:50051
```

## 2. Client Java depuis un autre laptop
Trouver l'IP du Laptop 1 (`ipconfig` / `ip a`), autoriser le port 50051 dans le pare-feu, puis :
```
cd java_client
mvn compile exec:java -Dexec.args="IP_DU_LAPTOP1 50051"
```
(`mvn compile` lance protoc via le plugin et génère les classes Java.)

## 3. Client 2 (Android / autre langage)
Même `primes.proto`, nouveau client avec les stubs générés pour le langage choisi
(sur Android : grpc-okhttp, `ManagedChannelBuilder.forAddress(IP, 50051).usePlaintext()`).
Sur l'émulateur Android, `10.0.2.2` désigne la machine hôte.
