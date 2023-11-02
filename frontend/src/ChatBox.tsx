import { useEffect, useState } from 'react'
import { Container, Row, Col } from 'react-bootstrap'
import * as io from 'socket.io-client'
//emit for sending
//on for reciveing
const socket = io.connect('http://localhost:4001')

interface ChatBoxProps {
  currentRoom: string
}

interface Message {
  content: string;
  timestamp: Date;
  senderId: string;
  color: string;
}


const ChatBox: React.FC<ChatBoxProps> = ({ currentRoom }) => {
  const [input, setInput] = useState('')
  const [messages, addMessage] = useState<Message[]>([])
  const [room, setRoom] = useState('default_room')

  const sendMessage = (event: React.FormEvent) => {
    event.preventDefault()
    if (input.trim() !== '') {
      console.log('sent')
      setRoom(currentRoom)
      socket.emit('send_message', room, input)
      setInput('')
    }
  }

  useEffect(() => {
    setRoom(currentRoom)
    addMessage([])
    socket.emit('join_room', room)
    socket.on('recieved_message', (message: Message) => {
      if (message.content !== '') {
        addMessage((messages) => [...messages, message])
        setInput('')
      }
    })

    return () => {
      socket.emit('leave_room', room)
      socket.off('recieved_message')
    }
  }, [room, currentRoom])

  return (
    <div className="chatbox-container">
      <h2>Chat</h2>
      <div className="chat-messages">
      {messages.map((message, index) => (
        <div key={index} className={message.senderId === socket.id ? 'message-right' : 'message-left'}>
          <p style={{ color: message.color }}>
            {message.content}
          </p>
          <span className="timestamp">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>
      ))}
      </div>
      <form className="chat-input-form" onSubmit={sendMessage}>
        <input
          type="text"
          value={input}
          className="chat-input"
          placeholder='Type Message'
          onChange={(event) => setInput(event.target.value)}
        />
        <button className="chat-send-button" type="submit">
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatBox;
