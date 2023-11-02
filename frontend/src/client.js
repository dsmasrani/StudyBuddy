const express = require('express');
const app = express();
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

app.use(cors());

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: 'http://localhost:5173',
    methods: ['GET', 'POST'],
  },
});

io.on('connection', (socket) => {
  console.log(`User connected: ${socket.id}`);

  console.log(`User connected: ${socket.id}`);

  socket.on('join_room', (room) => {
    socket.join(room);
    socket.color = '#' + Math.floor(Math.random() * 16777215).toString(16); 
    console.log(`User ${socket.id} joined room ${room}`);
  });


  socket.on('leave_room', (room) => {
    socket.leave(room);
    console.log(`User ${socket.id} left room ${room}`);
  });

  socket.on('send_message', (room, messageContent) => {
    const message = {
      content: messageContent,
      timestamp: new Date(),
      senderId: socket.id,
      color: socket.color
    };
    io.to(room).emit('recieved_message', message);
  });
});

server.listen(4001, () => {
  console.log('server connected');
});