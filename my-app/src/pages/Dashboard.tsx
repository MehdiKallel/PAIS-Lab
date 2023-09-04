import React, { useState, useEffect } from "react";
import io from "socket.io-client";
import OrderService from "../api/OrderService";

interface Order {
  _id: string;
  content: string;
  author_name: string;
}

interface Result {
  _id: string;
  rule: string;
  matched_orders: Order[];
}

const Dashboard: React.FC = () => {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [results, setResults] = useState<Result[] | null>(null);
  const [regex, setRegex] = useState<string>("");
  const [error, setError] = useState<string | null>(null); // New state for error

  useEffect(() => {
    const socket = io("http://localhost:4000");
    socket.on("db_update_orders", (updatedOrders: Order[]) => {
      setOrders(updatedOrders);
    });

    socket.on("db_update_results", (updatedResults: Result[]) => {
      setResults(updatedResults);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const applyRule = async () => {
    try {
      await OrderService.applyRule(regex);
      setRegex("");
      setError(null);
    } catch (e) {
      setError("Error");
    }
  };

  return (
    <div style={{ textAlign: 'left', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ fontSize: '2em', margin: '0.5em 0' }}>Orders Dashboard</h1>
      {error && <div style={{ color: 'red', margin: '0.5em 0' }}>{error}</div>}
      <h2 style={{ fontSize: '1.5em', margin: '0.5em 0' }}>Raw Text Orders</h2>
      <ul style={{ margin: '0.5em 0' }}>
        {Array.isArray(orders) && orders.map((order) => (
          <li key={order._id}>Author: {order.author_name} / Content: {order.content}</li>
        ))}
      </ul>
      <h2 style={{ fontSize: '1.5em', margin: '0.5em 0' }}>Results Queue</h2>
      {Array.isArray(results) && results.map((result, index) => (
        <div key={result._id} style={{ margin: '0.5em 0' }}>
          <h3 style={{ fontSize: '1.3em', margin: '0.5em 0' }}>Rule Match {index + 1}: {result.rule}</h3>
          <ul style={{ margin: '0.5em 0' }}>
            {result.matched_orders.map((order) => (
              <li key={order._id}>Order ID: {order._id} / Content: {order.content} / Author: {order.author_name}</li>
            ))}
          </ul>
        </div>
      ))}
      <h2 style={{ fontSize: '1.5em', margin: '0.5em 0' }}>Apply Rule</h2>
      <input
        type="text"
        value={regex}
        placeholder="Enter regex"
        onChange={(e) => setRegex(e.target.value)}
        style={{ margin: '0.5em 0' }}
      />
      <button onClick={applyRule} style={{ margin: '0.5em 0' }}>
        Apply
      </button>
    </div>
  );
};

export default Dashboard;
