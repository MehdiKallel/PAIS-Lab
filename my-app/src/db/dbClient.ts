import { Server, Socket } from "socket.io";
import { MongoClient, Collection, ChangeStream } from "mongodb";
import cors from "cors";
import express from "express";
import http from "http";

const app = express();
const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: "http://localhost:3000",
    methods: ["GET", "POST"],
  },
});

app.use(
  cors({
    origin: "http://localhost:3000",
  })
);

async function fetchAndEmitOrders(ordersCollection: Collection): Promise<void> {
  const orders = await ordersCollection.find({}).toArray();
  io.emit("db_update_orders", orders);
}

async function fetchAndEmitResults(resultsCollection: Collection): Promise<void> {
  const results = await resultsCollection.find({}).toArray();
  io.emit("db_update_results", results);
}

async function main(): Promise<void> {
  const uri = "mongodb+srv://admin:admin@cluster0.tlq7ewv.mongodb.net/";
  if (!uri) {
    throw new Error("Missing MONGODB_URI env var");
  }

  const client = new MongoClient(uri);
  await client.connect();

  const db_a = client.db("queue_a_db");
  const ordersCollection = db_a.collection("orders");

  const db_b = client.db("results_db");
  const resultsCollection = db_b.collection("results");

  fetchAndEmitOrders(ordersCollection);
  fetchAndEmitResults(resultsCollection);
  const ordersChangeStream: ChangeStream = ordersCollection.watch();
  ordersChangeStream.on("change", async () => {
    await fetchAndEmitOrders(ordersCollection);
  });

  const resultsChangeStream: ChangeStream = resultsCollection.watch();
  resultsChangeStream.on("change", async () => {
    await fetchAndEmitResults(resultsCollection);
  });
}

main().catch(console.error);

io.on("connection", (socket: Socket) => {
  console.log("New client connected");
});

server.listen(4000, () => {
  console.log("listening on *:4000");
});
